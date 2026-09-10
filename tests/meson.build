rounded_test = executable(
	'rounded-region-test',
	'rounded-region.c',
	'../sway/desktop/rounded.c',
	include_directories: sway_inc,
	dependencies: [pixman, math],
	c_args: ['-UNDEBUG'],
)
test('rounded-region', rounded_test)

scene_clip_test = executable(
	'scene-clip-test',
	'scene-clip.c',
	'../sway/desktop/rounded.c',
	include_directories: sway_inc,
	dependencies: [wlroots, pixman, math],
	c_args: ['-UNDEBUG', '-DWLR_PRIVATE='],
)
test('scene-clip', scene_clip_test)
