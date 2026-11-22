"""Export the existing sports north entry and west wing beside the revised Humanities model."""
import json

from build_complex import Model, OUTPUT, north_forecourt
from complex_details import roof_room
from sports import build as sports


def build():
    model = Model()
    model.section = "PE_North_Annex"
    sports(model, north_annex=True)
    roof_room(model, -318.25,509.0,15.79,4.7,3.4,2.50)
    roof_room(model, -318.43,518.22,14.87,2.45,2.70,1.23)
    north_forecourt(model, north_annex=True)
    model.save(OUTPUT / "pe_north_annex.glb", single_mesh=True)
    layout = OUTPUT / "pe_north_annex_collision.json"
    layout.write_text(json.dumps(model.solids, separators=(",",":")), encoding="utf-8")


if __name__ == "__main__":
    build()
