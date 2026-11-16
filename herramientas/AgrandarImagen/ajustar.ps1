# Lleva la imagen agrandada por la IA (x4) al tamano pedido, manteniendo la proporcion, y la guarda en PNG o JPG.
param([string]$Original, [string]$Grande, [string]$Salida, [string]$Modo, [int]$Valor)
Add-Type -AssemblyName System.Drawing
$o = [System.Drawing.Image]::FromFile((Resolve-Path $Original))
$W0 = $o.Width; $H0 = $o.Height; $o.Dispose()
$g = [System.Drawing.Image]::FromFile((Resolve-Path $Grande))
if ($Modo -eq 'factor') { $W = $W0 * $Valor; $H = $H0 * $Valor }
else {
  $k = $Valor / [math]::Max($W0, $H0)
  $W = [int][math]::Round($W0 * $k); $H = [int][math]::Round($H0 * $k)
}
if ($W -eq $g.Width -and $H -eq $g.Height) { $bmp = New-Object System.Drawing.Bitmap $g }
else {
  # mas grande que x4: se estira el resultado de la IA; mas chico: se reduce (queda mas nitido)
  $bmp = New-Object System.Drawing.Bitmap $W, $H, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $gr = [System.Drawing.Graphics]::FromImage($bmp)
  $gr.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $gr.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $gr.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $gr.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
  $ia = New-Object System.Drawing.Imaging.ImageAttributes
  $ia.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)        # sin bordes oscuros
  $gr.DrawImage($g, (New-Object System.Drawing.Rectangle 0, 0, $W, $H), 0, 0, $g.Width, $g.Height, [System.Drawing.GraphicsUnit]::Pixel, $ia)
  $gr.Dispose()
}
$g.Dispose()
if ($Salida.ToLower().EndsWith('.jpg')) {
  $enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
  $ps = New-Object System.Drawing.Imaging.EncoderParameters 1
  $ps.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 95L
  $rgb = New-Object System.Drawing.Bitmap $bmp.Width, $bmp.Height, ([System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $g2 = [System.Drawing.Graphics]::FromImage($rgb); $g2.Clear([System.Drawing.Color]::White); $g2.DrawImage($bmp, 0, 0, $bmp.Width, $bmp.Height); $g2.Dispose()
  $rgb.Save($Salida, $enc, $ps); $rgb.Dispose()
} else { $bmp.Save($Salida, [System.Drawing.Imaging.ImageFormat]::Png) }
$bmp.Dispose()
Write-Host ("     OK: {0}x{1} -> {2}x{3}  ->  {4}" -f $W0, $H0, $W, $H, $Salida)
