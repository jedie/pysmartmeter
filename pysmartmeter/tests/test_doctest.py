# import doctest
# from pathlib import Path
#
# import pysmartmeter
#
#
# def load_tests(loader, tests, ignore):
#     base_path = Path(pysmartmeter.__file__).parent
#     files = [str(p.relative_to(base_path)) for p in base_path.rglob('*.py')]
#     doc_test_suite = doctest.DocFileSuite(*files, package=pysmartmeter)
#     tests.addTests(doc_test_suite)
#     return tests
