#include <math.h>
#include "sway/rounded.h"

void rounded_rect_region(pixman_region32_t *region,
		int x, int y, int width, int height, int radius) {
	pixman_region32_clear(region);
	if (width <= 0 || height <= 0) {
		return;
	}
	radius = fmax(0, fmin(radius, fmin(width / 2, height / 2)));
	pixman_region32_union_rect(region, region,
		x, y + radius, width, height - 2 * radius);
	for (int row = 0; row < radius; ++row) {
		double dy = radius - row - 0.5;
		int inset = ceil(radius - sqrt((double)radius * radius - dy * dy) - 0.5);
		pixman_region32_union_rect(region, region,
			x + inset, y + row, width - 2 * inset, 1);
		pixman_region32_union_rect(region, region,
			x + inset, y + height - row - 1, width - 2 * inset, 1);
	}
}
