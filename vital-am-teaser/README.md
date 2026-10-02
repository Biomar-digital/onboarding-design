# Vital AM – teaser de vídeo (dirección 1)

Brief: *VN Brief Vital AM video teaser*, dirección 1 ("No one skips breakfast. Why would your shrimp?"). 10 s, 16:9 y 9:16.

## Mockup 3D del pack
- `mockup/SmartCare_Vital_AM_Bag.glb`: bolsa de 10 kg llena (≈41 × 72 × 22 cm) con el arte de Vital AM en frente y dorso. Usa la malla del mockup de SmartCare Assist Skin con el mismo ratio ancho/alto y más volumen.
- `mockup/vital_am_turntable.mp4`: vídeo giratorio de 360° (6 s).
- `mockup/vital_front.jpg`: textura 2048×2048. `mockup/vital_am_mockup_preview.jpg`: vista frontal.
- `tools/make_texture.py`: genera el mapa de sombreado suave a partir del mockup original.
- `tools/build_bag.py`: deforma la malla, recalcula las normales, ajusta el arte sin deformarlo y escribe el GLB.

## Plan de producción
| Fase | Herramienta | Créditos |
|---|---|---|
| 1. Previs 3D: estanque, pellets, camarones, cámara y pack | Higgsfield 3D Jutsu (Blender) | por confirmar |
| 2. Revisión de la previs | — | no |
| 3. Prueba de S2 y S3 (8 s, 480p) | Seedance 2.0 en modo fast con el previs como video_reference | sí, con presupuesto previo |
| 4. Versión final a 1080p | Seedance 2.0 en modo std | sí, con presupuesto previo |
| 5. Proyecto de After Effects: script `.jsx`, cámara de Blender y textos EN/VN | script y Adobe CC Files | no |

La S1 (reloj a las 6:30 sobre negro), los textos, la voz en off y el SFX se hacen en After Effects, no con IA.
