#include <assert.h>
#include <wlr/types/wlr_scene.h>
#include "sway/rounded.h"

int main(void) {
	struct wlr_scene *scene = wlr_scene_create();
	assert(scene);
	const float color[] = {1, 1, 1, 1};
	struct wlr_scene_rect *back = wlr_scene_rect_create(&scene->tree, 200, 200, color);
	struct wlr_scene_tree *tree = wlr_scene_tree_create(&scene->tree);
	struct wlr_scene_rect *front = wlr_scene_rect_create(tree, 40, 40, color);
	assert(back && tree && front);
	wlr_scene_node_set_position(&tree->node, 20, 30);
	pixman_region32_t clip;
	pixman_region32_init(&clip);
	rounded_rect_region(&clip, 0, 0, 40, 40, 12);
	wlr_scene_node_set_clip(&tree->node, &clip);
	assert(wlr_scene_node_at(&scene->tree.node, 20, 30, NULL, NULL) == &back->node);
	assert(wlr_scene_node_at(&scene->tree.node, 40, 50, NULL, NULL) == &front->node);
	// Opaque clients must not occlude the background outside their clip.
	assert(pixman_region32_contains_point(&back->node.visible, 20, 30, NULL));
	assert(!pixman_region32_contains_point(&back->node.visible, 40, 50, NULL));
	assert(!pixman_region32_contains_point(&front->node.visible, 20, 30, NULL));

	// A leaf clip intersects its ancestor's clip, with independent origins.
	rounded_rect_region(&clip, 10, 10, 20, 20, 0);
	wlr_scene_node_set_clip(&front->node, &clip);
	assert(wlr_scene_node_at(&scene->tree.node, 40, 31, NULL, NULL) == &back->node);
	assert(wlr_scene_node_at(&scene->tree.node, 40, 50, NULL, NULL) == &front->node);
	wlr_scene_node_set_position(&tree->node, 80, 90);
	assert(wlr_scene_node_at(&scene->tree.node, 40, 50, NULL, NULL) == &back->node);
	assert(pixman_region32_contains_point(&back->node.visible, 40, 50, NULL));
	assert(wlr_scene_node_at(&scene->tree.node, 100, 110, NULL, NULL) == &front->node);

	// Empty clips hide nodes, including changes made while disabled.
	wlr_scene_node_set_enabled(&tree->node, false);
	pixman_region32_clear(&clip);
	wlr_scene_node_set_clip(&front->node, &clip);
	wlr_scene_node_set_enabled(&tree->node, true);
	assert(wlr_scene_node_at(&scene->tree.node, 100, 110, NULL, NULL) == &back->node);
	wlr_scene_node_set_clip(&front->node, NULL);
	wlr_scene_node_set_clip(&tree->node, NULL);
	assert(wlr_scene_node_at(&scene->tree.node, 80, 90, NULL, NULL) == &front->node);
	assert(!pixman_region32_contains_point(&back->node.visible, 80, 90, NULL));
	wlr_scene_node_destroy(&tree->node);
	assert(pixman_region32_contains_point(&back->node.visible, 80, 90, NULL));
	pixman_region32_fini(&clip);
	wlr_scene_node_destroy(&scene->tree.node);
	return 0;
}
