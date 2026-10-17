import sys, os, unittest, tempfile, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from undercut_radar import extract, judge
from undercut_radar.config import Product, Competitor
from undercut_radar.store import Store
from undercut_radar import fetch

P = Product("X", 199.0, 180.0); C = Competitor("N", "u", 0.0)
D = pathlib.Path(__file__).parent.parent / "demo_pages"

class T(unittest.TestCase):
    def test_extract_jsonld(self): self.assertEqual(extract.extract((D / "northpeak_v2.html").read_text())["price"], 174.0)
    def test_extract_meta(self): self.assertEqual(extract.extract((D / "brightmart_v1.html").read_text())["price"], 204.0)
    def test_extract_markup_and_stock(self):
        d = extract.extract((D / "brightmart_v2.html").read_text()); self.assertEqual(d["price"], 204.0); self.assertFalse(d["in_stock"])
    def test_no_price_returns_none(self): self.assertIsNone(extract.extract("<html>captcha</html>"))
    def test_undercut_below_floor_is_hold(self):
        k, m, v = judge.judge(P, C, (174.0, 0.0, True), (189.0, 0.0, True)); self.assertEqual(k, "undercut"); self.assertTrue(v.startswith("HOLD"))
    def test_undercut_above_floor_can_match(self):
        k, m, v = judge.judge(P, C, (190.0, 0.0, True), (199.0, 0.0, True)); self.assertTrue(v.startswith("MATCH"))
    def test_shipping_counts(self):
        self.assertIsNone(judge.judge(P, Competitor("N", "u", 10.0), (195.0, 10.0, True), None))
    def test_same_undercut_does_not_repeat(self): self.assertIsNone(judge.judge(P, C, (174.0, 0.0, True), (174.0, 0.0, True)))
    def test_no_alert_when_not_cheaper(self): self.assertIsNone(judge.judge(P, C, (205.0, 0.0, True), (205.0, 0.0, True)))
    def test_out_of_stock_event(self):
        self.assertEqual(judge.judge(P, C, (204.0, 0.0, False), (204.0, 0.0, True))[0], "out_of_stock")
    def test_floor_is_never_broken(self): self.assertEqual(judge.never_below_floor(P, 150.0), 180.0)
    def test_store_roundtrip(self):
        s = Store(os.path.join(tempfile.mkdtemp(), "t.db")); r = fetch.FetchResult("u", 200, "x", .1)
        s.add_reading("X", C, r, {"price": 10.0, "method": "t"}); s.add_reading("X", C, r, {"price": 9.0, "method": "t"})
        self.assertEqual([x[0] for x in s.last_two("X", "N")], [9.0, 10.0])
if __name__ == "__main__": unittest.main()
