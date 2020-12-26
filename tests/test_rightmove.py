from unittest import TestCase

from crib.scraper.spiders.rightmove import extract_floor_area

class TestRightmoveSpider(TestCase):

    text = """ 

/-——
;

 

 

BEDROOM IS Al

14°6 x 9'4
4.4m x 2.8m = kK N

 

 

 

 

 

 

LOUNGE/DINER/KITCHEN
30'5 x 17'3
9.3m x 5.3m
BEDROOM
178 x 11'8
5.4m x 3.6m
1ST FLOOR

APPROX. FLOOR
AREA 523 SQ.FT.
(48.6 SQ.M.)

GROUND FLOOR
APPROX. FLOOR
AREA 570 SQ.FT.
(63.0 SQ.M.)
TOTAL APPROX. FLOOR AREA 1093 SQ.FT. (101.6 SQ.M.)
Whilst every attempt has been made to ensure the accuracy of the floor plan contained here, measurements
of doors, windows, rooms and any other items are approximate and no responsibility is taken for any error,
omission, of mis-statement. This plan is fo illustrative purposes only and should be used as such by any
prospective purchaser. The services, systems and appliances shown have not been tested and no guarantee
as to their operability or efficiency can be given
Made with Metropi 2015,

 

   
"""

    def test_get_area(self):
        area = extract_floor_area(self.text)
        self.assertEquals(area, 101.6)
