#include <errno.h>
#include <stdlib.h>
#include "sway/commands.h"
#include "sway/config.h"
#include "sway/tree/arrange.h"

struct cmd_results *cmd_floating_corner_radius(int argc, char **argv) {
	struct cmd_results *error = checkarg(argc, "floating_corner_radius",
		EXPECTED_EQUAL_TO, 1);
	if (error) {
		return error;
	}
	errno = 0;
	char *end;
	long radius = strtol(argv[0], &end, 10);
	if (errno || end == argv[0] || *end || radius < 0 || radius > 1000) {
		return cmd_results_new(CMD_INVALID,
			"Expected a corner radius between 0 and 1000");
	}
	config->floating_corner_radius = radius;
	arrange_root();
	return cmd_results_new(CMD_SUCCESS, NULL);
}
