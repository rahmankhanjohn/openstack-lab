import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'lab_status', Path(__file__).parent / 'lab-status.py')
lab_status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab_status)


class FakeProc:
    def __init__(self, stdout='', stderr='', returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class TestCountRows(unittest.TestCase):
    def test_counts_non_empty_lines(self):
        self.assertEqual(lab_status.count_rows('a\n\nb\n  \nc\n'), 3)

    def test_empty_string(self):
        self.assertEqual(lab_status.count_rows(''), 0)


class TestCheckAll(unittest.TestCase):
    def setUp(self):
        self.original = lab_status.run
        self.calls = []

    def tearDown(self):
        lab_status.run = self.original

    def test_reports_ok_when_everything_answers(self):
        def fake_run(command):
            self.calls.append(command)
            return 'row1\nrow2\n', None
        lab_status.run = fake_run
        results = lab_status.check_all()
        self.assertTrue(all(r['state'] == 'OK' for r in results))
        self.assertEqual(len(results), len(lab_status.CHECKS))

    def test_reports_fail_on_error(self):
        def fake_run(command):
            return None, 'command not found'
        lab_status.run = fake_run
        results = lab_status.check_all()
        self.assertTrue(all(r['state'] == 'FAIL' for r in results))

    def test_reports_empty_when_no_rows(self):
        def fake_run(command):
            return '', None
        lab_status.run = fake_run
        results = lab_status.check_all()
        self.assertTrue(all(r['state'] == 'EMPTY' for r in results))

    def test_render_mentions_the_failure_list(self):
        def fake_run(command):
            return None, 'command not found'
        lab_status.run = fake_run
        text = lab_status.render(lab_status.check_all())
        self.assertIn('Fix first:', text)

    def test_render_healthy_message(self):
        def fake_run(command):
            return 'row\n', None
        lab_status.run = fake_run
        text = lab_status.render(lab_status.check_all())
        self.assertIn('Lab looks healthy', text)


if __name__ == '__main__':
    unittest.main()
