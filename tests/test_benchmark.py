import os

from docker_starter import _generate_docker_compose


def test_generate_docker_compose_handles_dotted_paths(tmp_path, monkeypatch):
    work_dir = tmp_path / 'my.project'
    work_dir.mkdir()
    (work_dir / 'docker-compose-node.yaml').write_text('services:\n  validator-TAG:\n    networks: [NET_main-net]\n')
    monkeypatch.chdir(work_dir)

    file_name = _generate_docker_compose('./docker-compose-node.yaml', 3)

    assert file_name == './docker-compose-node-3.yaml'
    content = open(file_name).read()
    assert 'validator-3' in content
    assert 'my.project_main-net' in content
    assert os.path.exists('docker-compose-node-3.yaml')
