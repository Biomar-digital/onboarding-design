# Vital AM – teaser de vídeo (dirección 1)

Brief: *VN Brief Vital AM video teaser*, dirección 1 ("No one skips breakfast. Why would your shrimp?"). 10 s, 16:9 y 9:16.

## Mockup 3D del pack
- `mockup/SmartCare_Vital_AM_Bag.glb`: bolsa de 10 kg llena (≈41 × 72 × 22 cm) con el arte de Vital AM en frente y dorso. Usa la malla del mockup de SmartCare Assist Skin con el mismo ratio ancho/alto y más volumen.
- `mockup/vital_am_turntable.mp4`: vídeo giratorio de 360° (6 s).
- `mockup/vital_front.jpg`: textura 2048×2048. `mockup/vital_am_mockup_preview.jpg`: vista frontal.
- `tools/make_texture.py`: genera el mapa de sombreado suave a partir del mockup original.
- `tools/build_bag.py`: deforma la malla, recalcula las normales, ajusta el arte sin deformarlo y escribe el GLB.

## Previs y animatic (v1)
- `edit/VitalAM_teaser_animatic_v1.mp4`: animatic de 10 s en 16:9 con S1 (reloj a las 6:30 y pitido), S2 y S3 (previs), textos en VN y EN, subtítulos de la voz en off y cierre con "Vital AM – Sắp ra mắt".
- `previs/scene_r5.blend` y `previs/scene_r5.glb`: escena de Blender del proyecto de 3D Jutsu (revisión 5) con la cámara y la animación (8 s, 192 fotogramas a 24 fps).
- `previs/previs_local.mp4`: render del previs con la bolsa real (three.js en local, `previs.html` y `previs.mjs`).
- `edit/compose.py`: montaje del animatic (`python3 compose.py previs_local.mp4 salida.mp4`).

## Previs v2 (storyboard nuevo, sin textos)
`previs-v2/VitalAM_previs_v2.mp4`: 10 s a 24 fps en 5 planos, con un sonido de referencia (no es el audio final).

| Plano | Tiempo | Contenido |
|---|---|---|
| 1 | 0–1,5 s | Camarones en ayunas, quietos en el fondo; la alarma suena apagada bajo el agua |
| 2 | 1,5–3 s | Celular con la alarma de las 6:30 en la mesa de luz; la mano lo apaga (sin cara) |
| 3 | 3–5,5 s | Dron sobre el estanque al amanecer; de lejos, el granjero lanza los pellets con la pala azul |
| 4 | 5,5–8 s | Bajo el agua seguimos los pellets que se hunden; los camarones llegan a comer |
| 5 | 8–10 s | La bolsa en el muelle a contraluz; el sol sale por detrás y la revela |

Para renderizar: `node v2.mjs 0 239 1280 frames` (desde una carpeta con three.js, playwright-core y `SmartCare_Vital_AM_Bag.glb`). El sonido sale de `python3 sfx.py`.

## Previs v3 (hecha en Higgsfield 3D Jutsu)
`previs-v3/VitalAM_previs_v3.mp4`: 15 s a 24 fps (360 fotogramas), sin textos, con un sonido de referencia. La escena es el proyecto de 3D Jutsu `ea6989d5-d5b5-4049-80fc-fbf854d815c7` (revisión 10). El render se hace en local con three.js a partir del GLB que exporta Higgsfield.

| Plano | Fotogramas | Contenido |
|---|---|---|
| 1 | 1–48 | Camarones en ayunas en el fondo del estanque (agua lechosa gris azulada); la alarma se oye apagada |
| 2 | 49–96 | Alarma real de las 6:30 en el celular; solo se ve la mano que la apaga |
| 3 | 97–180 | Dron sobre el estanque al amanecer (aireadores de paletas, palmeras, pasarela); de lejos, el granjero lanza el alimento con la pala azul |
| 4 | 181–300 | Seguimos los pellets mientras se hunden (unos 3–5 s); los camarones los buscan con las antenas, los agarran con las patas y comen en el fondo |
| 5 | 301–360 | Salimos del agua: la bolsa a contraluz y el sol que sale por detrás y la revela |

Cambios según la investigación (L. vannamei) y el video de referencia:
- Pellets de 2 mm que se hunden despacio.
- Camarones que descansan en el fondo y escapan con un coletazo.
- Búsqueda en zigzag hasta agarrar el pellet.
- Cardúmenes densos a media agua.
- Estanque con liner de HDPE de 1,5 m de profundidad y transparencia baja.

Renderizar: `node v3.mjs 1 360 1280 frames`, con `scene_v3_r9.glb` y `SmartCare_Vital_AM_Bag.glb` al lado. El sonido sale de `python3 sfx_v3.py`.

## Previs v4 (correcciones sobre la v3)
`previs-v4/VitalAM_previs_v4.mp4`: la escena es la revisión 12 del mismo proyecto de 3D Jutsu.
- **Titileo resuelto:** los pellets se agrandaban en cada fotograma y se veían desde el principio. Ahora aparecen y desaparecen según sus propios tiempos.
- **Pellets de tamaño real:** 2 a 4 mm; en el aire, al doble para que se lean.
- **Pala de mano azul y lanzamiento de costado con un brazo**, como en la foto de referencia. Son 4 tandas de 90 pellets que forman un arco en abanico.
- **Partículas del agua:** ahora son un polvillo claro y fino, no bolas grises.
- **Plano 5:** el horizonte queda abierto detrás de la bolsa y el sol sale desde atrás de ella.
- **Plano 3:** el dron termina más cerca, por detrás del granjero.
- **Agua y mano:** el agua del dron es verde lechosa y la mano del plano 2 ya no se ve negra.

Renderizar: `node v4.mjs 1 360 1280 frames`, con `scene_v4.glb` (revisión 12) y `SmartCare_Vital_AM_Bag.glb` al lado. El sonido sale de `python3 sfx_v4.py`.

## Previs v7 (modelo de camarón del cliente)
`previs-v7/VitalAM_previs_v7.mp4`: la escena es la revisión 22 del proyecto de 3D Jutsu.
- **Camarones:** el modelo riggeado del cliente (`Shrimp_Anim_01_AE.glb`, con ciclo de nado "ShrimpSwim") reemplaza a los 98 camarones. Se escala a 13,7 cm, sigue las trayectorias de la escena y la velocidad del nado depende de la velocidad real de cada camarón.
  - Higgsfield no deja importar modelos propios, así que el modelo se compone en el render local (`v7.html`).
- **Sin superposiciones:** cada cuerpo es una cápsula (del rostro al telson) y las colisiones se resuelven en cada fotograma (`collision_pass.py`). La auditoría independiente sobre el GLB exportado (`overlap.mjs`) da 0 pares en 360 fotogramas.
- **Plano 4:** el camarón protagonista llega al pellet desde atrás y come de frente a la cámara. Hay un cono despejado entre la cámara y el pellet (fotogramas 262 a 300) y un acercamiento de 32 a 56 mm.
- **Planos 4 y 5:** un solo movimiento de cámara, sin corte, del fondo del estanque a la superficie y hasta la bolsa.
- **Celular:** la vibración es más suave y la pantalla ya no titila.

## Previs v8 (mano nueva, un solo tiro y cámara que sigue al feed bajo el agua)
`previs-v8/VitalAM_previs_v8.mp4`: la escena es la revisión 27 del proyecto de 3D Jutsu.
- **Plano 2, la mano:** se rehízo desde cero (`hand_tap_v3.py`).
  - El índice va extendido y la yema cae justo sobre el botón STOP en el fotograma 84.
  - Los otros tres dedos van recogidos bajo la palma, con el pulgar apoyado sobre ellos.
  - La muñeca va elevada unos 26° y el dorso no tiene abolladuras.
- **Plano 3, un solo tiro:** el farmer tira una sola vez con la pala (suelta en el fotograma 160) y la pala se vacía una sola vez (`single_throw.py`).
- **Planos 3 y 4, un solo movimiento de cámara** (`camera_follow_feed_dive.py`):
  1. el drone baja por detrás del hombro del farmer;
  2. sigue la nube de pellets a unos 30 cm durante todo el arco;
  3. entra al agua donde caen (fotograma 196) y baja junto a los pellets que se hunden;
  4. gira bajo el agua hasta empalmar sin corte con la toma del camarón comiendo (fotograma 236).
- **Lente:** pasa de 24 a 32 mm durante la bajada.
- **Sonido de referencia:** un solo barrido de pala, la lluvia de pellets sobre el agua, el golpe de la cámara al entrar y burbujeo apagado (`sfx_v8.py`).

## Previs v9 y prueba de Seedance
- `previs-v9/`: los pellets nunca tocan el fondo y los camarones comen siempre a media agua (`pellets_in_water_column.py`).
- `seedance/`: primer borrador de Seedance 2.5 a 480p (45 créditos), con los prompts y las referencias usadas.

## Previs v10 (pellet del cliente, cámara más fluida y match cut)
`previs-v10/VitalAM_previs_v10.mp4`: la escena es la revisión 34 del proyecto de 3D Jutsu.
- **Pellet del cliente:** el modelo `pellet_F_poroso_alto_4K.glb` se usa a 3 mm de largo, que es su tamaño real. Se simplificó a unos 14.500 triángulos y, de lejos, pasa a una esfera.
- **Un solo pellet protagonista** (`hero_pellet_camera.py`): la cámara sigue el mismo pellet desde la pala, por el aire, al agua y hasta el camarón que lo atrapa a media agua.
  - Va a su lado, a unos 11 cm.
  - El suavizado se calcula relativo al pellet para que no se salga de cuadro.
  - Lente: 24 → 35 → 32 mm.
- **Transición del despertador al estanque (match cut):** después de apagar la alarma, la cámara sube hasta quedar cenital sobre el celular apagado. Corta a un plano cenital del dron a 44 m: el estanque es el mismo rectángulo oscuro, con la misma orientación. Desde ahí el dron se inclina en espiral hasta el hombro del farmer y sigue sin corte con el pellet (`commit_v10.py`).
  - La mano sale más rápido después del toque.
  - La pantalla apagada tiene un brillo cálido sutil.
- **Sin superposiciones:** la pasada de colisiones se volvió a correr con la nueva trayectoria y la auditoría da 0 cuadros con superposición.
- **Sonido de referencia** (`sfx_v10.py`): el ambiente del estanque entra 8 cuadros antes del corte (J-cut), con un soplo de aire que crece sobre la subida al cenital. La lluvia de pellets y la entrada al agua están sincronizadas con el cuadro 189.

Renderizar: `node v10.mjs 1 360 1280 frames` (desde una carpeta con `scene_v10.glb`, `user_shrimp.glb`, `user_pellet_lod.glb` y `SmartCare_Vital_AM_Bag.glb`).

## Plan de producción
| Fase | Herramienta | Créditos |
|---|---|---|
| 1. Previs 3D: estanque, pellets, camarones, cámara y pack | Higgsfield 3D Jutsu (Blender) | por confirmar |
| 2. Revisión de la previs | — | no |
| 3. Prueba de S2 y S3 (8 s, 480p) | Seedance 2.0 en modo fast con el previs como video_reference | sí, con presupuesto previo |
| 4. Versión final a 1080p | Seedance 2.0 en modo std | sí, con presupuesto previo |
| 5. Proyecto de After Effects: script `.jsx`, cámara de Blender y textos EN/VN | script y Adobe CC Files | no |

La S1 (reloj a las 6:30 sobre negro), los textos, la voz en off y el SFX se hacen en After Effects, no con IA.
