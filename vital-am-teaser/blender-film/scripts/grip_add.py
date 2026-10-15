# Farmer's right hand -> HF fist (index curled) that actually closes around the scoop handle; hide the open rig hand.
import bpy
S='/tmp/claude-0/-home-user-onboarding-design/47d2e554-3fba-5f2b-903d-37793a6dfe1a/scratchpad/'
bpy.ops.wm.open_mainfile(filepath=S+'film/film.blend')
before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=S+'hf/fist.glb')
new=[o for o in bpy.data.objects if o not in before]; f=[o for o in new if o.type=='MESH'][0]
for o in new:
    if o is not f: bpy.data.objects.remove(o)
mw=f.matrix_world.copy(); f.parent=None; f.matrix_world=mw; f.name='FIST'
b=bpy.data.objects['FARMER_BODY']
# soften the auto-rig's pinching at shoulder / armpit / elbow
cs=b.modifiers.new('CorrectiveSmooth','CORRECTIVE_SMOOTH'); cs.factor=0.6; cs.iterations=12; cs.smooth_type='LENGTH_WEIGHTED'; cs.rest_source='ORCO'
m=b.modifiers.new('HideRightHand','MASK'); m.vertex_group='RightHand'; m.invert_vertex_group=True; m.threshold=0.8   # mask AFTER the smooth (CorrectiveSmooth needs the full vertex count)
# feed in the bucket: heap of brown pellets instead of a flat black disc; bucket gets moulded-plastic micro texture
bf=bpy.data.objects['BUCKET_FEED']; fm=bpy.data.materials.new('MAT_FeedHeap'); fm.use_nodes=True; nt=fm.node_tree; b2=nt.nodes['Principled BSDF']; L=nt.links
tc=nt.nodes.new('ShaderNodeTexCoord'); vo=nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=260; L.new(tc.outputs['Object'],vo.inputs['Vector'])
rp=nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color=(0.20,0.12,0.06,1); rp.color_ramp.elements[1].color=(0.05,0.03,0.015,1); rp.color_ramp.elements[1].position=0.9; L.new(vo.outputs['Distance'],rp.inputs[0])
L.new(rp.outputs[0],b2.inputs['Base Color']); b2.inputs['Roughness'].default_value=0.8
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=1.0; bp.inputs['Distance'].default_value=0.004; bp.invert=True; L.new(vo.outputs['Distance'],bp.inputs['Height']); L.new(bp.outputs[0],b2.inputs['Normal'])
bf.data.materials.clear(); bf.data.materials.append(fm)
bk=bpy.data.objects['BUCKET_BODY'].active_material
if bk and bk.use_nodes:
    nt=bk.node_tree; bb=[x for x in nt.nodes if x.type=='BSDF_PRINCIPLED'][0]; nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=180
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.08; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs[0],bb.inputs['Normal']); bb.inputs['Roughness'].default_value=0.45
bpy.ops.wm.save_as_mainfile(filepath=S+'film/film.blend'); print('GRIP_OK',[x.name for x in b.modifiers])
