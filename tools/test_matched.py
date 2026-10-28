import unittest

from build_matched import mineral_pixels


class MineralMask(unittest.TestCase):
    def test_every_mineral_shade_is_retained_and_rock_stays_dark(self):
        rock = bytes([100, 100, 100, 255, 140, 140, 140, 255])
        ore = rock + bytes([35, 25, 15, 255, 180, 120, 80, 255, 70, 150, 130, 255])
        result = mineral_pixels(ore, rock)
        self.assertEqual(result[:8], bytes(8))
        self.assertEqual(result[8:], ore[8:])

    def test_coal_is_not_lost_by_a_color_saturation_filter(self):
        rock = bytes([100, 100, 100, 255])
        coal = bytes([20, 20, 20, 255, 40, 40, 40, 255])
        self.assertEqual(mineral_pixels(coal, rock, kind='coal', coal_ceiling=75), coal)

    def test_neutral_edge_pixels_not_in_plain_stone_are_not_mineral(self):
        rock = bytes([100, 100, 100, 255])
        edges = bytes([90, 90, 90, 255, 160, 160, 160, 255])
        copper = bytes([220, 110, 60, 255, 60, 150, 120, 255])
        self.assertEqual(mineral_pixels(edges + copper, rock), bytes(8) + copper)

    def test_pale_mineral_highlights_are_kept_but_tinted_rock_bevels_are_not(self):
        rock = bytes([100, 100, 100, 255])
        pale = bytes([220, 245, 230, 255])
        tinted = bytes([145, 138, 138, 255])
        self.assertEqual(mineral_pixels(pale + tinted, rock, {(220, 245, 230)}), pale + bytes(4))

    def test_coal_rock_edge_is_not_selected_just_because_it_is_gray(self):
        rock = bytes([100, 100, 100, 255])
        edge = bytes([90, 90, 90, 255])
        self.assertEqual(mineral_pixels(edge, rock, kind='coal', coal_ceiling=75), bytes(4))

    def test_quartz_does_not_include_red_netherrack_bevels(self):
        rock = bytes([100, 40, 40, 255])
        edge = bytes([170, 110, 105, 255])
        quartz = bytes([230, 225, 218, 255, 110, 85, 65, 255])
        self.assertEqual(mineral_pixels(edge + quartz, rock, kind='quartz'), bytes(4) + quartz)

    def test_transparent_pixels_never_become_emissive(self):
        self.assertEqual(mineral_pixels(bytes([255, 0, 0, 0]), bytes([100, 100, 100, 255])), bytes(4))


if __name__ == '__main__':
    unittest.main()
