"""Commercial source semantics and malformed-input regressions for ROM gate."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rom_gate', ROOT / 'skills/rom/scripts/rom_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class ROMGatePreservation(unittest.TestCase):
    def setUp(self):
        self.fig = json.loads((ROOT / 'skills/rom/scripts/fixtures/rom_pass.json').read_text())
    def test_independent_fixed_fee_may_differ_from_hourly_billings(self):
        self.fig['quote_total_fee'] = 320000
        self.assertEqual([], gate.check(self.fig)[1])
    def test_fixed_fee_requires_both_source_and_basis(self):
        for field in ('fee_source', 'fixed_fee_basis'):
            for value in (None, '', ' ', 7, []):
                with self.subTest(field=field, value=value):
                    fig = copy.deepcopy(self.fig); fig[field] = value
                    self.assertTrue(gate.check(fig)[1])
    def test_tm_reconciles_and_rejects_mismatch(self):
        self.fig.update(pricing_model='t_and_m', model_card='tm_envelope')
        self.assertFalse(gate.check(self.fig)[1])
        self.fig['quote_total_fee'] = 320000
        self.assertTrue(gate.check(self.fig)[1])
    def test_all_numeric_fields_reject_nonfinite_negative_and_wrong_types(self):
        for field in ('quote_total_hours','blended_rate','quote_total_fee','range_low','range_high'):
            for value in (-1, float('nan'), float('inf'), '1200', True, None, [], 10**400):
                with self.subTest(field=field,value=repr(value)):
                    fig = copy.deepcopy(self.fig); fig[field] = value
                    self.assertTrue(gate.check(fig)[1])
    def test_nested_hours_and_malformed_rows_fail_with_diagnostics(self):
        for field in ('phases','roles','work_packages'):
            for rows in (None, {}, [1], [{}], [{'hours':v} for v in [1]]):
                if rows == [{'hours':1}]:
                    continue
                fig=copy.deepcopy(self.fig); fig[field]=rows
                self.assertTrue(gate.check(fig)[1])
            for value in (-1,float('nan'),float('inf'), '1200', True, None):
                fig=copy.deepcopy(self.fig); fig[field]=[{'hours':value}]
                self.assertTrue(gate.check(fig)[1])
    def test_invalid_root_and_model_types_do_not_crash(self):
        for value in (None, [], 3, 'text'):
            self.assertTrue(gate.check(value)[1])
        for field in ('q_number','pricing_model','model_card'):
            fig=copy.deepcopy(self.fig); fig[field]=[]
            self.assertTrue(gate.check(fig)[1])
    def test_finite_operands_that_overflow_fail(self):
        self.fig.update(quote_total_hours=1e308,blended_rate=1e308,pricing_model='t_and_m',model_card='tm_envelope')
        self.fig['phases']=[{'hours':1e308},{'hours':1e308}]
        self.assertTrue(gate.check(self.fig)[1])
    def test_packaged_original_selftest(self):
        self.assertEqual(0, gate.selftest())

if __name__ == '__main__': unittest.main()
