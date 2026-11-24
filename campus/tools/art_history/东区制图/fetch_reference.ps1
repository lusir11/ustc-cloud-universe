param([int]$zoom,[int]$x0,[int]$x1,[int]$y0,[int]$y1,[string]$name)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$d=(Resolve-Path '原项目东区正射图').Path
$canvas=[Drawing.Bitmap]::new(256*($x1-$x0+1),256*($y1-$y0+1)); $g=[Drawing.Graphics]::FromImage($canvas)
$client=[Net.Http.HttpClient]::new(); $client.Timeout=[TimeSpan]::FromSeconds(15)
for($y=$y0;$y -le $y1;$y++){for($x=$x0;$x -le $x1;$x++){
 $url="https://map.ustc.edu.cn/mapdata/zoom$zoom/${x}_$y.jpg"
 $bytes=$client.GetByteArrayAsync($url).GetAwaiter().GetResult()
 $s=[IO.MemoryStream]::new($bytes); $im=[Drawing.Image]::FromStream($s)
 $g.DrawImageUnscaled($im,256*($x-$x0),256*($y-$y0));$im.Dispose();$s.Dispose()
}}
$canvas.Save("$d/$name.jpg",[Drawing.Imaging.ImageFormat]::Jpeg)
$w=960; $h=[int]($canvas.Height*$w/$canvas.Width)
$preview=[Drawing.Bitmap]::new($canvas,$w,$h); $preview.Save("$d/$name-small.jpg",[Drawing.Imaging.ImageFormat]::Jpeg); $preview.Dispose()
$g.Dispose();$canvas.Dispose();$client.Dispose()
