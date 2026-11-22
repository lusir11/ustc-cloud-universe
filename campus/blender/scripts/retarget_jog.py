"""Replace only the campus student's run clip with Quaternius' CC0 Jog.

The CC0 KinemIQ release supplies KinemIQ_Mannequin.glb (the bind pose) and
Run_jog_forwards.glb (the motion). Run this from desktop Python with NumPy
and SciPy. The game asset retains its original skeleton and all other clips.
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import struct

import numpy as np
from scipy.spatial.transform import Rotation


class Glb:
    def __init__(self, path):
        raw = path.read_bytes()
        magic, version, size, json_size, chunk = struct.unpack_from('<4sIII4s', raw)
        if (magic, version, size, chunk) != (b'glTF', 2, len(raw), b'JSON'):
            raise ValueError(f'Invalid GLB: {path}')
        self.doc = json.loads(raw[20:20+json_size])
        self.data = bytearray(raw[28+json_size:])
        self.nodes = self.doc['nodes']
        self.index = {node['name']: i for i, node in enumerate(self.nodes) if 'name' in node}
        self.parent = {child: i for i, node in enumerate(self.nodes) for child in node.get('children', [])}

    def read(self, index):
        spec = self.doc['accessors'][index]
        view = self.doc['bufferViews'][spec['bufferView']]
        dtype = np.dtype({5121:'u1', 5123:'<u2', 5125:'<u4', 5126:'<f4'}[spec['componentType']])
        width = {'SCALAR':1, 'VEC3':3, 'VEC4':4, 'MAT4':16}[spec['type']]
        offset = view.get('byteOffset', 0) + spec.get('byteOffset', 0)
        stride = view.get('byteStride', width * dtype.itemsize)
        values = np.ndarray((spec['count'], width), dtype, self.data, offset, (stride, dtype.itemsize))
        return values.astype(float) / np.iinfo(dtype).max if spec.get('normalized') else values.copy()

    def add_track(self, values):
        values = np.asarray(values, dtype='<f4')
        views, accessors = self.doc['bufferViews'], self.doc['accessors']
        payload = values.tobytes()
        views.append({'buffer':0, 'byteOffset':len(self.data), 'byteLength':len(payload)})
        self.data.extend(payload)
        accessors.append({'bufferView':len(views)-1, 'componentType':5126,
                          'count':len(values), 'type':{1:'SCALAR',3:'VEC3',4:'VEC4'}[values.shape[1]],
                          'min':values.min(axis=0).tolist(), 'max':values.max(axis=0).tolist()})
        return len(accessors)-1

    def bind(self, skin):
        return np.linalg.inv(self.read(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1))

    def write(self, path):
        self.doc['buffers'][0]['byteLength'] = len(self.data)
        header = json.dumps(self.doc, separators=(',', ':'), ensure_ascii=False).encode('utf8')
        header += b' ' * (-len(header) % 4)
        result = struct.pack('<4sIII4s', b'glTF', 2, 28+len(header)+len(self.data), len(header), b'JSON')
        temp = path.with_suffix('.tmp')
        temp.write_bytes(result+header+struct.pack('<I4s',len(self.data),b'BIN\0')+self.data)
        temp.replace(path)


def source_world(asset):
    clip, = asset.doc['animations']
    tracks = {}
    times = None
    for channel in clip['channels']:
        sampler = clip['samplers'][channel['sampler']]
        track_times = asset.read(sampler['input'])
        if times is not None and not np.array_equal(times, track_times):
            raise ValueError('Expected common sample times for the source jog.')
        times = track_times
        tracks[channel['target']['node'],channel['target']['path']] = asset.read(sampler['output'])
    world = {}

    def visit(i):
        if i not in world:
            n = asset.nodes[i]
            local = np.broadcast_to(np.eye(4), (len(times),4,4)).copy()
            local[:,:3,:3] = Rotation.from_quat(tracks.get((i,'rotation'), n.get('rotation',[0,0,0,1]))).as_matrix()
            local[:,:3,3] = tracks.get((i,'translation'), n.get('translation',[0,0,0]))
            world[i] = visit(asset.parent[i]) @ local if i in asset.parent else local
        return world[i]

    return times, {name:visit(i) for name,i in asset.index.items()}


def contact_samples(asset, sides):
    """Keep only the sole vertices needed to evaluate the lowest point."""
    result = []
    for node in asset.nodes:
        if 'skin' not in node or not node.get('name','').startswith(sides):
            continue
        skin = asset.doc['skins'][node['skin']]
        inverse = np.linalg.inv(asset.bind(skin))
        for shape in asset.doc['meshes'][node['mesh']]['primitives']:
            attrs = shape['attributes']
            xyz = asset.read(attrs['POSITION'])
            bottom = xyz[:,1] < xyz[:,1].min()+0.050
            points = np.column_stack((xyz[bottom],np.ones(np.count_nonzero(bottom))))
            joints = asset.read(attrs['JOINTS_0'])[bottom]
            weights = asset.read(attrs['WEIGHTS_0'])[bottom]
            used = [asset.nodes[n]['name'] for n in skin['joints']]
            local = (inverse[joints] @ points[:,None,:,None])[...,0]
            result.append((used,joints,weights,local))
    if not result:
        raise ValueError('No foot geometry available to align the run to the ground.')
    return result


def sole_height(world, samples):
    heights = []
    for names,joints,weights,local in samples:
        rows = np.stack([world[name][:,1,:] for name in names],axis=1)
        skinned = np.sum(rows[:,joints]*local[None,:,:,:],axis=-1)
        heights.append(np.min(np.sum(skinned*weights[None,:,:],axis=2),axis=1))
    return np.min(heights,axis=0)


def match_rotation(source_pose, source_bind, target_bind, direction_match):
    correction = np.eye(3)
    if direction_match:
        start, end = target_bind[:,1], source_bind[:,1]
        axis = np.cross(start,end)
        length = np.linalg.norm(axis)
        if length > 1e-7:
            correction = Rotation.from_rotvec(axis*np.arctan2(length,np.dot(start,end))/length).as_matrix()
    return source_pose @ source_bind.T @ correction @ target_bind


def retarget(target, mannequin, jog):
    time, motion = source_world(jog)
    src_skin = mannequin.doc['skins'][0]
    src_bind = {mannequin.nodes[i]['name']:mat for i,mat in zip(src_skin['joints'],mannequin.bind(src_skin))}
    skin = target.doc['skins'][0]
    target_bind = dict(zip(skin['joints'], target.bind(skin)))
    mapping = {'Hips':'pelvis', 'Spine':'spine_02', 'Chest':'spine_03', 'Neck':'neck_01', 'Head':'Head'}
    limbs = {'Clavicle':'clavicle','UpperArm':'upperarm','Forearm':'lowerarm',
             'Hand':'hand','Thigh':'thigh','Shin':'calf','Foot':'foot','Toe':'ball'}
    for side in ('L','R'):
        mapping.update({name+'.'+side:src+'_'+side.lower() for name,src in limbs.items()})
    positions, world, tracks = {}, {}, {}
    direction_bones = {'UpperArm','Forearm','Hand','Thigh','Shin'}

    def evaluate(i):
        if i in world:
            return world[i]
        bone = target.nodes[i]['name']
        parent = target.parent[i]
        if parent in target_bind:
            parent_pose = evaluate(parent)
            bind_local = np.linalg.solve(target_bind[parent], target_bind[i])
        else:
            parent_pose = np.broadcast_to(np.eye(4),(len(time),4,4))
            bind_local = target_bind[i]
        position = np.broadcast_to(bind_local[:3,3],(len(time),3)).copy()
        rotation = np.broadcast_to(bind_local[:3,:3],(len(time),3,3))
        if bone in mapping:
            reference = mapping[bone]
            src_rot = motion[reference][:,:3,:3]
            absolute = match_rotation(src_rot, src_bind[reference][:3,:3], target_bind[i][:3,:3],
                                      bone.split('.')[0] in direction_bones)
            rotation = parent_pose[:,:3,:3].transpose(0,2,1) @ absolute
        if bone=='Hips':
            hips = motion['pelvis'][:,:3,3]
            progress = time / time[-1,0]
            remainder = hips - (hips[0]+progress*(hips[-1]-hips[0]))
            position[:,0] += (remainder[:,0]-np.mean(remainder[:-1,0]))*.8
            position[:,2] += np.clip(remainder[:,2]-np.mean(remainder[:-1,2]),-.035,.035)
        matrix = np.broadcast_to(np.eye(4),(len(time),4,4)).copy()
        matrix[:,:3,:3] = rotation
        matrix[:,:3,3] = position
        positions[bone] = position
        quaternion = Rotation.from_matrix(rotation).as_quat()
        for k in range(1,len(quaternion)):
            if np.dot(quaternion[k-1],quaternion[k]) < 0:
                quaternion[k] *= -1
        quaternion[-1] = np.copysign(1,np.dot(quaternion[-2],quaternion[0]))*quaternion[0]
        tracks[i,'rotation'] = quaternion
        world[i] = parent_pose @ matrix
        return world[i]

    for bone in target_bind:
        evaluate(bone)
    world_by_name = {target.nodes[i]['name']:pose for i,pose in world.items()}
    original_height = sole_height(motion,contact_samples(mannequin,('SuperHero_Male',)))
    target_height = sole_height(world_by_name,contact_samples(target,('Shoe_Upper','Shoe_Sole')))
    # Preserve the source flight phase, while matching the campus character's
    # shorter legs and sneaker thickness to the contact plane.
    reference_ground = np.percentile(original_height[:-1],20)
    clearance = np.maximum(0,original_height-reference_ground-.004)*.88
    hip_pos = positions['Hips']
    hip_pos[:,1] += clearance-target_height+.003
    hip_pos[-1] = hip_pos[0]
    tracks[target.index['Hips'],'translation'] = hip_pos
    run = next(clip for clip in target.doc['animations'] if clip['name']=='run')
    dense_time = target.add_track(time)
    constant_time = target.add_track(time[[0,-1]])
    for channel in run['channels']:
        sampler = run['samplers'][channel['sampler']]
        key = channel['target']['node'],channel['target']['path']
        if key in tracks:
            sampler.update(input=dense_time,output=target.add_track(tracks[key]),interpolation='LINEAR')
        else:
            sampler['input'] = constant_time
    run['extras'] = {'source':'Quaternius Universal Animation Library / KinemIQ CC0 GLB',
                     'clip':'Jog_Fwd_Loop', 'license':'CC0-1.0',
                     'url':'https://github.com/Kinemiq/free-game-animations/releases/tag/v1.0'}
    print('Loop seconds',round(float(time[-1,0]),4),
          'foot clearance range',np.round([clearance.min(),clearance.max()],3),
          'pelvis height range',np.round([hip_pos[:,1].min(),hip_pos[:,1].max()],3))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('campus_asset',type=Path)
    parser.add_argument('source_directory',type=Path)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    actor = Glb(args.campus_asset)
    retarget(actor,Glb(args.source_directory/'KinemIQ_Mannequin.glb'),
             Glb(args.source_directory/'Run_jog_forwards.glb'))
    actor.write(args.output)


if __name__ == '__main__':
    main()
