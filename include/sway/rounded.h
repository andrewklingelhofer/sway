#ifndef _SWAY_ROUNDED_H
#define _SWAY_ROUNDED_H
#include <pixman.h>

// Replace an initialized region with a rounded rectangle, in output pixels.
// The radius is clamped to half the shorter edge. Pixels are sampled at their
// centers, so opposite corners have identical coverage.
void rounded_rect_region(pixman_region32_t *region,
	int x, int y, int width, int height, int radius);

#endif
