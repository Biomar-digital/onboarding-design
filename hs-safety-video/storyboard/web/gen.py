import html
S=[
 ("1","Why incident reporting matters","0:00","0:28",[
  ("1A","img/e1_produccion.jpg","0:00","Every day, we work together to create a safe workplace.","Production operator checking the line at the control panel. Guards closed, full PPE.","Slow push-in."),
  ("1B","img/s1b_deposito.jpg","0:05","Most incidents can be prevented if we identify risks early and learn from our experiences. That's why it is important to report safety incidents, including hazards and near misses, whenever they occur.","Warehouse operator scanning a pallet from the pedestrian side of the racking.","Lateral slide along the racking."),
  ("1C","img/s1c_oficina_workday.jpg","0:18","To make it as easy as possible, all employees can report safety incidents directly in Workday.","Office: employee opens a laptop to start Workday. Screen faces away; the real Workday screen comes in Scene 4.","Gentle push-in toward the laptop."),
 ]),
 ("2","What is a safety incident?","0:28","1:13",[
  ("2·0",None,"0:28","There are different types of incidents, including:","Title card on light-blue background.","Motion graphic","On screen: “What is a safety incident?”"),
  ("2A","img/s2a_lesion_caida.jpg","0:32","Personal injuries, such as cuts, burns, strains or fractures.","PERSONAL INJURY: operator slips on spilled liquid. Not graphic, no blood.","Quick freeze-frame at the moment of the slip.","Label: Personal injury"),
  ("2B","img/s2b_peligro_derrame_v2.jpg","0:39","Hazards, such as damaged equipment, spills, blocked walkways or other unsafe conditions that could cause harm.","HAZARD: liquid leaking from a cracked hose onto the walkway. No people.","Slow tilt down from the hose to the puddle.","Label: Hazard"),
  ("2C","img/e2_casi_accidente.jpg","0:49","Near misses, where an incident could have resulted in injury or damage but luckily did not.","NEAR MISS: an overhanging box falls from the racking and lands more than a metre away. Nobody is hit.","Box falls in real time, short hold on the operator's reaction.","Label: Near miss"),
  ("2D",None,"0:57","Although hazards and near misses do not always result in consequences, reporting them helps us identify risks and take action before someone gets hurt.","The three examples shrink into cards and connect with lines to one central box.","Motion graphic","Cards: Personal injury · Hazard · Near miss → central box: Safety Incident"),
 ]),
 ("3","What should you do?","1:13","1:58",[
  ("3A","img/e3_cartel_derrame.jpg","1:13","If an incident occurs, your first priority is always safety. Make the area safe if possible.","Operator places a wet-floor sign at the edge of the spill, standing on dry floor.","Medium shot, small push-in.","Icon: warning sign"),
  ("3B","img/s3a_asistir_lesionado_v2.jpg","1:24","Seek assistance if someone is injured. Follow local emergency procedures when required.","Colleague kneels next to the injured operator on dry floor and calls for help on the radio. Does not move him.","Static, slight drift.","Icon: first aid / radio"),
  ("3C","img/s3c_aviso_supervisora_v2.jpg","1:40","Inform your supervisor or manager as soon as possible.","Operator explains what happened to the shift supervisor; the marked-off spill is visible behind them.","Slow arc around the two.","Icon: speech bubble"),
 ]),
 ("4","How to report in Workday","1:58","3:28",[
  ("4A","img/e4_celular_v3.jpg","1:58","As an employee, you can report safety incidents directly in Workday. This can help make sure that key information is recorded as soon as possible. You can do it on a computer or directly on your phone, making it quick and easy to submit a report.","Operator standing still in a safe area off the traffic route, glove off, phone in hand.","Push-in toward the phone, then cut into the screen."),
  ("4·1",None,"2:12","To report a safety incident, open Workday and click on “Report Safety Incident” in your menu.","Screen recording: open Workday → menu → Report Safety Incident.","Your screen recording, framed in an illustrated phone","Highlight: Report Safety Incident"),
  ("4·2",None,"2:20","Or search for “Report Safety Incident” in the search bar.","Screen recording: type the search term in the search bar.","Screen recording","Highlight: search bar"),
  ("4·3",None,"2:26","Complete the fields, including: business unit and site, incident date and time, incident type, area, and fill in the summary, describing what happened. Remember not to include names or other personal details in the summary.","Screen recording: zoom on each field in turn with its call-out.","Screen recording + call-outs","Location: In which business unit and site did the incident happen? · Incident date and time: When did the incident happen? · Incident type: What type of incident? · Incident location: In what area did the incident happen? · Summary: Describe what happened and leave out names and other personal information"),
  ("4B","img/s4b_foto_derrame_v3.jpg","2:58","If possible, upload photos and then submit the report.","Operator taps “Take photo” and photographs the spill with both hands from outside the puddle, gloves tucked in the vest pocket. Sign already in place.","Over-the-shoulder, then the photo appears in the form.","Highlight: Take photo"),
  ("4·4",None,"3:06","","Screen recording: attachment shown, tap Submit, confirmation.","Screen recording","Highlight: Submit"),
  ("4C","img/s4c_safety_partner_revisa_v2.jpg","3:12","Once submitted, the report is reviewed by the Health & Safety responsible in your business unit.","Safety Partner reviewing the new report and its photo at her desk.","Slow push-in over the shoulder."),
 ]),
 ("5","Closing","3:28","3:55",[
  ("5A","img/s5a_exterior_planta.jpg","3:28","Every report makes a difference.","Another site: two operators walking on the marked walkway outside a coastal feed plant.","Wide, slow lateral move."),
  ("5B","img/s5b_oficina_reunion_v2.jpg","3:32","By reporting incidents, you help protect your colleagues…","Supervisor and Safety Partner reviewing the improvement trend.","Static, gentle drift."),
  ("5C","img/f01_elenco_v2.jpg","3:38","…and contribute to a safer workplace for everyone.","The whole team in the production hall, inside the walkway.","Slow pull-back."),
  ("5·E",None,"3:45","","End screen with the BioMar logo.","Motion graphic","See it. · Report it. · Prevent it."),
 ]),
]
def card(f):
    fid,img,tc,vo,vis,cam=f[:6]; ost=f[6] if len(f)>6 else ""
    if img: media=f'<img src="{img}" alt="Frame {fid}: {html.escape(vis)}" loading="lazy" width="1280" height="720">'
    else:
        kind="Screen recording" if "Screen recording" in cam else "Motion graphic"
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
