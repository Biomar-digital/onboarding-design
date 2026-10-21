import html
S=[
 ('1','Why incident reporting matters','0:00','0:25',[
  ('1A', 'img/e1_produccion.jpg', '0:00', 'Together, we can create a safer workplace by learning from every hazard, near miss and incident.', 'Production operator checking the line at the control panel. Guards closed, full PPE.', 'Slow push-in.'),
  ('1B', 'img/s1b_deposito.jpg', '0:09', 'When you report what you see or experience, you help us identify risks early and prevent future harm.', 'Warehouse operator scanning a pallet from the pedestrian side of the racking.', 'Lateral slide along the racking.'),
  ('1C', 'img/s1c_oficina_workday.jpg', '0:19', 'Reporting is quick and easy for everyone in Workday.', 'Office: employee opens a laptop to start Workday. Screen faces away; the real Workday screen comes in Scene 4.', 'Gentle push-in toward the laptop.'),
 ]),
 ('2','What is a safety incident?','0:25','1:10',[
  ('2·0', None, '0:25', 'Safety events can take different forms, including:', 'Title card on light-blue background.', 'Motion graphic', 'On screen: “What is a safety incident?”'),
  ('2A', 'img/s2a_lesion_caida.jpg', '0:32', 'Injuries, such as cuts, burns, strains or fractures.', 'PERSONAL INJURY: operator slips on spilled liquid. Not graphic, no blood.', 'Quick freeze-frame at the moment of the slip.', 'Label: Personal injury'),
  ('2B', 'img/s2b_peligro_derrame_v2.jpg', '0:37', 'Hazards, such as damaged equipment, spills, blocked walkways or other unsafe conditions that could cause harm.', 'HAZARD: liquid leaking from a cracked hose onto the walkway. No people.', 'Slow tilt down from the hose to the puddle.', 'Label: Hazard'),
  ('2C', 'img/e2_casi_accidente.jpg', '0:46', 'Near misses, where no one was hurt and nothing was damaged, but easily could have been.', 'NEAR MISS: an overhanging box falls from the racking and lands more than a metre away. Nobody is hit.', "Box falls in real time, short hold on the operator's reaction.", 'Label: Near miss'),
  ('2D', None, '0:55', 'Even when a hazard or near miss causes no harm, reporting it gives us the opportunity to learn, address the risk and help keep everyone safe.', 'The three examples shrink into cards and connect with lines to one central box.', 'Motion graphic', 'Cards: Personal injury · Hazard · Near miss → central box: Safety Incident'),
 ]),
 ('3','What should you do?','1:10','1:55',[
  ('3A', 'img/e3_cartel_derrame.jpg', '1:10', 'If an incident occurs, your first priority is to prevent further injury or material damage. If it is safe to do so, stop the activity, secure the area and take any immediate action needed to protect people and create a safe workplace.', 'Operator stops the activity and places a wet-floor sign at the edge of the spill, standing on dry floor.', 'Medium shot, small push-in.', 'Icon: warning sign'),
  ('3B', 'img/s3a_asistir_lesionado_v2.jpg', '1:32', 'Help anyone who is injured, seek assistance and follow local emergency procedures.', 'Colleague kneels next to the injured operator on dry floor and calls for help on the radio. Does not move him.', 'Static, slight drift.', 'Icon: first aid / radio'),
  ('3C', 'img/s3c_aviso_supervisora_v2.jpg', '1:41', 'Once the situation is safe and under control, it is time to report: inform your supervisor or manager as soon as possible and submit the incident report in Workday.', 'Operator explains what happened to the shift supervisor; the marked-off spill is visible behind them.', 'Slow arc around the two.', 'Icon: speech bubble'),
 ]),
 ('4','How to report in Workday','1:55','3:25',[
  ('4A', 'img/e4_celular_v3.jpg', '1:55', 'As an employee, you can report safety incidents directly in Workday, helping ensure that important information is recorded promptly. You can report from your computer or phone, whichever is most convenient.', 'Operator standing still in a safe area off the traffic route, glove off, phone in hand.', 'Push-in toward the phone, then cut into the screen.'),
  ('4·1', None, '2:10', 'To get started, just open Workday and select “Report Safety Incident” from the menu.', 'Screen recording: open Workday → menu → Report Safety Incident.', 'Your screen recording, framed in an illustrated phone', 'Highlight: Report Safety Incident'),
  ('4·2', None, '2:20', 'You can also search for “Report Safety Incident” using the search bar.', 'Screen recording: type the search term in the search bar.', 'Screen recording', 'Highlight: search bar'),
  ('4·3', None, '2:27', 'You just need to complete the following fields: business unit and site; date and time of the incident; type of incident; area where the incident occurred; and a brief summary of what happened. Please do not include names or other personal information.', 'Screen recording: zoom on each field in turn with its call-out.', 'Screen recording + call-outs', 'Location: In which business unit and site did the incident happen? · Incident date and time: When did the incident happen? · Incident type: What type of incident? · Incident location: In what area did the incident happen? · Summary: Describe what happened and leave out names and other personal information'),
  ('4B', 'img/s4b_foto_derrame_v3.jpg', '2:55', 'If it is safe and relevant, you can also upload photos before submitting the report.', 'Operator taps “Take photo” and photographs the spill with both hands from outside the puddle, gloves tucked in the vest pocket. Sign already in place.', 'Over-the-shoulder, then the photo appears in the form.', 'Highlight: Take photo'),
  ('4·4', None, '3:03', '', 'Screen recording: attachment shown, tap Submit, confirmation.', 'Screen recording', 'Highlight: Submit'),
  ('4C', 'img/s4c_safety_partner_revisa_v2.jpg', '3:11', 'After you submit the report, your local Health & Safety representative will review it, investigate the incident, ensure relevant corrective actions are taken and follow up as needed.', 'Safety Partner reviewing the new report and its photo at her desk.', 'Slow push-in over the shoulder.'),
 ]),
 ('5','Closing','3:25','3:47',[
  ('5A', 'img/s5a_exterior_planta.jpg', '3:25', 'Every report makes a difference.', 'Another site: two operators walking on the marked walkway outside a coastal feed plant.', 'Wide, slow lateral move.'),
  ('5B', 'img/s5b_oficina_reunion_v2.jpg', '3:29', 'By reporting incidents, you help protect your colleagues…', 'Supervisor and Safety Partner reviewing the improvement trend.', 'Static, gentle drift.'),
  ('5C', 'img/f01_elenco_v2.jpg', '3:34', '…and contribute to a safer workplace for everyone.', 'The whole team in the production hall, inside the walkway.', 'Slow pull-back.'),
  ('5·E', None, '3:39', '', 'End screen with the BioMar logo.', 'Motion graphic', 'See it. · Report it. · Prevent it.'),
 ]),
]
def card(f):
    fid,img,tc,vo,vis,cam=f[:6]; ost=f[6] if len(f)>6 else ""
    if img: media=f'<img src="{img}" alt="Frame {fid}: {html.escape(vis)}" loading="lazy" width="1280" height="720">'
    else:
        kind="Screen recording" if "screen recording" in cam.lower() else "Motion graphic"
        media=f'<div class="ph"><span class="ph-k">{kind}</span><span class="ph-t">{html.escape(ost or vis)}</span></div>'
    vo_html=f'<blockquote class="vo">{html.escape(vo)}</blockquote>' if vo else '<p class="vo none">No voice-over (music only)</p>'
    ost_html=f'<div class="row"><span class="k">On screen</span><span>{html.escape(ost)}</span></div>' if ost else ''
    return f'''<article class="frame"><div class="media">{media}</div><div class="meta">
<div class="fh"><span class="fid">{fid}</span><span class="tc">{tc}</span></div>
<div class="row"><span class="k">Voice-over</span>{vo_html}</div>
<div class="row"><span class="k">Action</span><span>{html.escape(vis)}</span></div>
<div class="row"><span class="k">Camera</span><span>{html.escape(cam)}</span></div>{ost_html}</div></article>'''
body=""
for n,t,a,b,fr in S:
    body+=f'<section class="scene" id="scene-{n}"><header class="sh"><span class="sn">Scene {n}</span><h2>{html.escape(t)}</h2><span class="sr">{a} – {b}</span></header>'+"".join(card(f) for f in fr)+'</section>'
page=open('tpl.html').read().replace('%%BODY%%',body)
open('index.html','w').write(page)
