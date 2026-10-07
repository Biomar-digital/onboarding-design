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

## Previs v11 (pellets que se comen, cámara pegada al pellet y match cut limpio)
`previs-v11/VitalAM_previs_v11.mp4`: sin sonido. Usa la escena de la revisión 34 y el renderer `v11.html`.
- **Un solo sistema de pellets** (1.173 por palada):
  - Cada pellet sale de la pala con una trayectoria balística y cae en abanico.
  - Deja un anillo de salpicadura en la superficie y se hunde frenando, sin llegar nunca al fondo.
  - Los pellets aparecen recién cuando salen de la pala; ya no aparecen de la nada.
- **Los camarones comen:** 72 camarones reciben un pellet que llega exactamente a su boca.
  - Lo comen en 6 mordiscos, con migas que caen.
  - El protagonista (`SHRIMP_05`) come en primer plano de perfil, con el pellet entre las patas delanteras.
- **Cámara:**
  - Sigue al pellet protagonista desde que sale de la pala: centrado, a unos 7,5 cm y con lente de 50 mm.
  - Lo ve contra el cielo mientras sube y contra el agua mientras cae.
  - Entra al agua con él, entre burbujas, y lo acompaña mientras se hunde hasta la boca del camarón.
- **Match cut:** el celular apagado es un rectángulo negro sobre la mesa, iluminada por la luz del amanecer. La cámara baja hacia él y, en el corte, el dron sigue bajando hacia el estanque, que ocupa el mismo lugar del cuadro y tiene la misma orientación. Ya no está el punto de luz sobre la pantalla.
- **Agua:** bajo la superficie es verde grisácea y turbia, igual que el estanque visto desde arriba.
- **Camarones:**
  - Nadan casi horizontales, con una inclinación máxima de unos 34°.
  - La auditoría (`v11audit.mjs`) da 0 cuadros con superposición en los 360.

Renderizar: `node v11.mjs 1 360 1280 frames` (desde la carpeta del previs v10, con los mismos GLB).

## Previs v12 (más tiempo y más claro)
`previs-v12/VitalAM_previs_v12.mp4`: 19,4 s (465 cuadros), sin sonido. Usa el mismo renderer, con las correcciones de abajo.
- **Más tiempo:** cada parte respira más. El vuelo del pellet va en cámara lenta (velocidad 0,6), y la bajada bajo el agua, la comida y la subida a la bolsa son más largas.
- **Celular:** la luz fría del amanecer no cambia al apagar la alarma. El celular apagado se lee como un vidrio negro con el reflejo de la ventana; la mano se retira y la cámara baja en cenital. Corta al estanque oscuro, del mismo tamaño y con la misma orientación.
- **Vuelo:** la cámara va a altura constante junto al pellet, que se ve contra el cielo sin que el horizonte salte, y recién al final ve venir el agua.
- **Bajo el agua:** el agua es más clara, así que los camarones aparecen debajo del pellet mientras se hunde. La cámara no suelta el pellet hasta la boca del camarón.
- **Comida:** el pellet llega a la boca real del modelo del camarón (punto calibrado). La cámara gira al perfil y se abre para mostrarlo comiendo.
- **Subida:** se acortó el tramo gris vacío antes de la bolsa.
- **Camarones:** 0 superposiciones en todos los cuadros, medidas sobre el eje real del cuerpo.

## Previs v13 (match cut exacto, granjero legible, final que se entiende)
`previs-v13/VitalAM_previs_v13.mp4`: unos 20 s (495 cuadros), sin sonido. Renderer `v12.html`.
- **Pantalla del celular:** al apagar la alarma solo desaparecen los elementos de la alarma (sin texto). La pantalla sigue encendida en el mismo azul, así que la luz del cuarto no cambia.
- **Match cut exacto:** la pantalla mide 2,22:1, así que el estanque de alimentación se alargó a 66,7 × 30 m (2,22:1) y la granja lo acompaña.
  - El dron abre a 64 m, en cenital, y el estanque refleja el cielo del amanecer en el mismo azul que la pantalla. Medido en el render: pantalla (48, 97, 199) y estanque (48, 97, 199).
  - El rectángulo ocupa la misma posición y el mismo tamaño en el cuadro (x 107–532 contra 108–531). Los estanques vecinos quedan oscuros, como la mesa alrededor del celular.
- **Granjero:** figura legible (camisa, pantalón, botas, cuello, sombrero cónico de paja claro y balde azul con alimento). El dron baja hasta un plano medio de tres cuartos de frente, con el sol detrás de la cámara. Ese momento dura más: se lo ve cargar la pala y lanzar.
- **Pellets:** 4 mm. Bajo el agua tienen un brillo cálido sutil para leerse contra los camarones, sin perder el marrón.
- **Final:** después de que el protagonista atrapa el pellet, la cámara se abre a un plano del grupo comiendo. Los camarones se ven a tamaño medio, no gigantes, y se entiende que comen pellets.

## Previs v14 (final como plano secuencia, escala como el video de referencia)
`previs-v14/VitalAM_previs_v14.mp4`: unos 21 s (502 cuadros), sin sonido. Renderer `v13.html`.
- **El camarón atrapa el pellet** con la cámara a unos 25 cm. Antes era un primer plano macro donde el camarón se veía gigante.
- **El grupo comiendo**, como el video de referencia (`Shrimp_Grower_Water`):
  - La cámara queda a unos 70 cm, a la altura del grupo y mirando apenas hacia arriba.
  - El agua es lechosa y gris azulada, con la luz detrás, así que camarones y pellets se leen como siluetas.
  - Cada camarón ocupa más o menos 1/5 del ancho del cuadro.
- **Subida sin corte hasta la bolsa:** la cámara sube en diagonal hacia el muelle, cuyos postes se ven bajo el agua. Sale a la superficie frente al muelle y encuadra la bolsa a contraluz con el sol saliendo. Se eliminó el viaje gris vacío del final anterior.

## Previs v15 (contrapicado, camarones comiendo a media agua y el 6:30)
`previs-v15/VitalAM_previs_v15.mp4`: unos 21 s, sin sonido. Renderer `v14.html`.
- **6:30:** la hora vuelve a verse en el celular mientras suena la alarma y desaparece con el botón al apagarla. La pantalla queda azul lisa para el match cut.
- **Contrapicado:** bajo el agua la cámara baja por debajo del pellet y lo sigue mirando hacia arriba, recortado contra la superficie clara. Los camarones comiendo y el plano del grupo también se ven desde abajo, como en el video de referencia.
- **Comen a media agua:** entre los cuadros 200 y 262 todo el grupo sube 50 cm desde el fondo hacia el alimento que cae. Es un mismo desplazamiento vertical para todos, así que la auditoría sigue dando 0 superposiciones.
- **Subida a la bolsa:** la cámara pasa por debajo del grupo hacia el muelle antes de subir, sin atravesar camarones.

## Previs v16 (final con camarones legibles, sin choques de cámara)
`previs-v16/VitalAM_previs_v16.mp4`: unos 19,5 s, sin sonido. Renderer `v15.html`.
- **Camarones translúcidos:** gris verdosos, con segmentos, ojos y patas visibles. Bajo el agua hay una luz frontal suave y las sombras se aclararon; antes eran siluetas negras.
- **El grupo aparece debajo del pellet** mientras sube hacia el alimento. El protagonista entra de perfil y atrapa el pellet con el resto del grupo alrededor, a tamaño medio, como en el video de referencia.
- **Cámara de la atrapada:** se elige automáticamente el lado alrededor del protagonista que queda libre de cuerpos, tanto en la bajada como en la atrapada y la salida. La cámara converge a esa posición desde la bajada, sin giros a último momento.
- **Anticolisión de cámara:** la trayectoria submarina se precalcula y se corre suavemente si algún camarón queda a menos de 17 cm. La distancia mínima a un cuerpo es de 12,5 cm y no hay ningún cuadro con un camarón atravesando la cámara.
- **Menos pellets a la deriva** (520): antes parecían polvo.
- **Salida:** la cámara sube frente al cardumen, sale a la superficie y vuela rasante sobre el agua hasta la bolsa a contraluz.
- **Ritmo:** la bajada del pellet se aceleró para que el grupo entre antes.
- 0 superposiciones entre camarones en todos los cuadros.

## Previs v17 (giro alrededor del granjero, camarones vistos desde arriba, salida suave)
`previs-v17/VitalAM_previs_v17.mp4`: unos 20 s, sin sonido. Renderer `v16.html`; render completo con `render_v17.sh`.
- **Granjero:**
  - Se lo ve de frente mientras carga la pala. Tiene cara simple y camisa con botones, para que se lea que está de frente.
  - La cámara gira a su alrededor por el lado de la pala y queda detrás de él justo cuando lanza. Ahí acompaña el revoleo y sigue los pellets.
  - El brazo izquierdo ahora cuelga natural al costado; antes quedaba clavado detrás del hombro.
- **El pellet protagonista sale de la pala** y se une a su trayectoria sin saltar. Antes aparecía de golpe a 2,4 m de altura y la cámara pegaba un tirón.
- **Comida:** la cámara mira un poco desde arriba, a 50 cm del camarón protagonista. Ningún otro camarón pasa a menos de 26 cm de la lente, así que no hay "gigantes".
- **Pellets que parecían pegados a los camarones:** eran pellets a la deriva que atravesaban los cuerpos. Ahora rodean cada cuerpo.
- **Salida del agua:** disolvencia de 15 cuadros entre una pasada bajo el agua y otra sobre el agua, para que el cruce de la superficie no sea brusco.
- **Final:** acercamiento lento y estable a la bolsa, con un arco suave y el sol subiendo detrás. Ese tramo va más lento (velocidad 0,5).
- 0 superposiciones entre camarones en todos los cuadros.

## Previs v18 (final rehecho: grupo comiendo, salida mitad y mitad y plano final de la bolsa)
`previs-v18/VitalAM_previs_v18.mp4`: unos 20,7 s, sin sonido. Renderer `v17.html`; final con `render_v18.sh`.
- **Grupo comiendo con el alimento cayendo:** plano casi nivelado a unos 60 cm del cardumen, con un desplazamiento lento. Los pellets siguen hundiéndose despacio entre los camarones y se desvanecen antes del fondo (nunca lo tocan). Se quitaron las manchas de arena del fondo en estos planos.
- **Salida del agua suave, con un plano mitad bajo el agua y mitad sobre el agua:** la cámara sube y frena en la superficie. Durante unos 21 cuadros, una línea de agua ondulada baja por el cuadro: arriba se ven el muelle, la bolsa y el amanecer; abajo, el agua y los postes. Lo componen `v17ou.mjs` y `ou_comp.py` a partir de dos pasadas (bajo y sobre el agua), con el horizonte submarino alineado a la línea del agua.
- **Plano final de la bolsa:** la cámara sube a la altura de la bolsa y se acerca despacio sobre el agua, con zoom lento de 28 a 42 mm. La bolsa queda entera en el cuadro, con el sol subiendo detrás.
- 0 superposiciones entre camarones en todos los cuadros.

## Previs v19 (dron con plano general de la granja, final en un solo arco)
`previs-v19/VitalAM_previs_v19.mp4`: unos 21,5 s, sin sonido. Renderer `v18.html`; render con `render_v19.sh`.
- **Dron:**
  - Se queda más tiempo en cenital sobre el estanque, con una bajada lenta.
  - Después baja en curva hasta un plano general de la granja: el granjero chico en el muelle, el galpón, las palmeras y el amanecer detrás.
  - Se acerca desacelerando hasta quedar de frente al granjero, y de ahí sale el giro alrededor de él hasta quedar detrás en el lanzamiento.
  - La trayectoria es un spline suavizado. El dron y el giro miran al mismo punto del granjero, así que no hay saltos.
- **Salto de los 16–17 s:** había quedado activo un tramo de cámara viejo, que primero tiraba hacia la posición de grupo anterior y después saltaba a la nueva. Se eliminó: la cámara pasa de la atrapada al grupo y a la subida en un solo movimiento continuo.
- **Salida a la bolsa en una sola parábola:**
  - Una curva Bézier continua: sube desde el grupo, cruza la superficie (con un leve frenado, sin detenerse), se eleva y baja suave hacia la bolsa.
  - El zoom es leve; ya no hay un empuje recto aparte.
  - El cruce de la superficie es el plano mitad bajo el agua y mitad sobre el agua. La imagen bajo el agua entra sin desplazamiento.
- **Saltos medidos cuadro a cuadro:** solo quedan los cortes previstos (al celular, el match cut y la entrada al agua).

## Plan de producción
| Fase | Herramienta | Créditos |
|---|---|---|
| 1. Previs 3D: estanque, pellets, camarones, cámara y pack | Higgsfield 3D Jutsu (Blender) | por confirmar |
| 2. Revisión de la previs | — | no |
| 3. Prueba de S2 y S3 (8 s, 480p) | Seedance 2.0 en modo fast con el previs como video_reference | sí, con presupuesto previo |
| 4. Versión final a 1080p | Seedance 2.0 en modo std | sí, con presupuesto previo |
| 5. Proyecto de After Effects: script `.jsx`, cámara de Blender y textos EN/VN | script y Adobe CC Files | no |

La S1 (reloj a las 6:30 sobre negro), los textos, la voz en off y el SFX se hacen en After Effects, no con IA.
