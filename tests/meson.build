rounded_test = executable(
	'rounded-region-test',
	'rounded-region.c',
	'../sway/desktop/rounded.c',
	include_directories: sway_inc,
	dependencies: [pixman, math],
	c_args: ['-UNDEBUG'],
)
test('rounded-region', rounded_test)
