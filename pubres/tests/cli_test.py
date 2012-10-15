from pubres.cli_arguments import make_parser


p = make_parser()


def test_command_line():
    r = p.parse_args(['--host', 'localhost', '--port', '5678', '--loglevel', 'ERROR'])
    assert r.host == 'localhost'
    assert r.port == 5678
    assert r.loglevel == 'ERROR'


def test_default_command_line():
    r = p.parse_args([])
    assert r.host == '127.0.0.1'
    assert r.port == 5555
    assert r.loglevel == 'INFO'
