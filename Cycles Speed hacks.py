bl_info = {
    "name": "Cycles CPU Speed Hacks",
    "author": "Blossom",
    "version": (1, 2, 0),
    "blender": (5, 0, 0),
    "location": "Properties > Render > Emerald Speed Hacks",
    "description": "Ultra-fast Cycles CPU settings (~12s target, 2K textures, true off-screen GI)",
    "category": "Render",
}

import bpy


class RENDER_OT_apply_cycles_speed_hacks(bpy.types.Operator):
    """Apply ultra-fast Cycles CPU optimizations with 2K textures"""
    bl_idname = "render.apply_cycles_speed_hacks"
    bl_label = "Apply Ultra-Fast Cycles (2K)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        cycles = scene.cycles
        render = scene.render

        # 1. Switch to Cycles & CPU
        render.engine = 'CYCLES'
        cycles.device = 'CPU'

        # 2. 75% HD Resolution (1440x810 - cuts pixel count by 44%)
        render.resolution_x = 1920
        render.resolution_y = 1080
        render.resolution_percentage = 75

        # 3. Ultra-Lean Sampling + Scrambling Distance + OpenImageDenoise
        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.08
        cycles.samples = 16
        if hasattr(cycles, "scrambling_distance"):
            cycles.scrambling_distance = 0.5
        if hasattr(cycles, "use_adaptive_scrambling_distance"):
            cycles.use_adaptive_scrambling_distance = True

        cycles.use_denoising = True
        cycles.denoiser = 'OPENIMAGEDENOISE'
        cycles.denoising_input_passes = 'RGB_ALBEDO'
        cycles.denoising_prefilter = 'FAST'

        # 4. Light Paths (True off-screen GI & reflections, zero waste)
        cycles.max_bounces = 3
        cycles.diffuse_bounces = 2
        cycles.glossy_bounces = 2
        cycles.transmission_bounces = 2
        cycles.volume_bounces = 0
        cycles.transparent_max_bounces = 4
        cycles.sample_clamp_direct = 10.0
        cycles.sample_clamp_indirect = 3.0

        if hasattr(cycles, "caustics_reflective"):
            cycles.caustics_reflective = False
        if hasattr(cycles, "caustics_refractive"):
            cycles.caustics_refractive = False

        # 5. Fast GI Approximation
        cycles.use_fast_gi = True
        cycles.fast_gi_method = 'REPLACE'
        cycles.ao_bounces = 1
        cycles.ao_bounces_render = 1

        # 6. Memory & CPU Performance
        render.use_persistent_data = True
        cycles.use_auto_tile = True
        cycles.tile_size = 512

        # 7. Simplify & Camera Culling (2K Texture Cap)
        render.use_simplify = True
        render.simplify_subdivision = 1
        render.simplify_subdivision_render = 2
        cycles.use_camera_cull = True
        cycles.camera_cull_margin = 0.2
        cycles.texture_limit_render = '2048'

        self.report({'INFO'}, "Emerald Force: Ultra-fast Cycles settings applied!")
        return {'FINISHED'}


class RENDER_PT_emerald_speed_panel(bpy.types.Panel):
    """Creates a Panel in the Render Properties window"""
    bl_label = "Cycles Speed Hacks"
    bl_idname = "RENDER_PT_emerald_speed_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.4
        col.operator("render.apply_cycles_speed_hacks", icon='SHADERFX')


classes = (
    RENDER_OT_apply_cycles_speed_hacks,
    RENDER_PT_emerald_speed_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
