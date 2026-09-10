#include <assert.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include "sway/rounded.h"

static bool expected(int x, int y, int width, int height, int radius) {
	if (x < 0 || y < 0 || x >= width || y >= height) {
		return false;
	}
	radius = fmax(0, fmin(radius, fmin(width / 2, height / 2)));
	double px = x + 0.5, py = y + 0.5;
	double cx = fmax(radius, fmin(px, width - radius));
	double cy = fmax(radius, fmin(py, height - radius));
	return (px - cx) * (px - cx) + (py - cy) * (py - cy) <= radius * radius;
}

int main(void) {
	pixman_region32_t shape, inner, border, overlap;
	pixman_region32_init(&shape);
	pixman_region32_init(&inner);
	pixman_region32_init(&border);
	pixman_region32_init(&overlap);
	// Odd sizes, tiny windows, negative origins, radius zero, and clamping.
	for (int width = 0; width < 36; ++width) {
		for (int height = 0; height < 36; ++height) {
			for (int radius = 0; radius < 24; ++radius) {
				rounded_rect_region(&shape, -13, 17, width, height, radius);
				for (int y = -1; y <= height; ++y) {
					for (int x = -1; x <= width; ++x) {
						assert(pixman_region32_contains_point(&shape,
							x - 13, y + 17, NULL) == expected(x, y, width, height, radius));
					}
				}
			}
		}
	}
	// A pixel border and content partition the shape without double blending.
	rounded_rect_region(&shape, 100, 200, 800, 600, 24);
	rounded_rect_region(&inner, 102, 202, 796, 596, 22);
	pixman_region32_subtract(&border, &shape, &inner);
	pixman_region32_intersect(&overlap, &border, &inner);
	assert(!pixman_region32_not_empty(&overlap));
	pixman_region32_union(&overlap, &border, &inner);
	assert(pixman_region32_equal(&overlap, &shape));
	assert(!pixman_region32_contains_point(&shape, 100, 200, NULL));
	assert(pixman_region32_contains_point(&border, 500, 200, NULL));
	assert(pixman_region32_contains_point(&inner, 500, 202, NULL));

	pixman_region32_fini(&overlap);
	pixman_region32_fini(&border);
	pixman_region32_fini(&inner);
	pixman_region32_fini(&shape);
	return 0;
}
