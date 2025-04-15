from sqlalchemy.orm import Session

from infra.db.models.fupgen import FupGen


def test_create_fupgen(populated_session: Session):

    session = populated_session
    fupgen_db = session.query(FupGen).filter_by(id="id1").first()
    assert fupgen_db is not None
    assert fupgen_db.name == "Test FupGen"
    assert fupgen_db.message.msg == "helloworld"
    assert fupgen_db.data.data == {"datakey": "datavalue"}


def test_read_fupgen(populated_session: Session):
    """Teste de leitura de um FupGen existente."""

    session = populated_session

    fupgen_db = session.query(FupGen).filter_by(id="id1").first()

    assert fupgen_db is not None
    assert fupgen_db.name == "Test FupGen"
    assert fupgen_db.description == "Some test description"


def test_read_fupgen_no_existent(populated_session: Session):
    """Teste de leitura de um FupGen não existente."""

    session = populated_session

    fupgen_db = session.query(FupGen).filter_by(id="noexistentid").all()

    assert fupgen_db == []


def test_update_fupgen(populated_session: Session):
    """Teste de atualização de um FupGen existente."""

    session = populated_session

    # Atualizando o FupGen
    fupgen_db = session.query(FupGen).filter_by(id="id1").first()
    fupgen_db.name = "FupGen Updated"
    session.commit()

    # Verificando se foi atualizado corretamente
    fupgen_updated = session.query(FupGen).filter_by(id="id1").first()
    assert fupgen_updated.name == "FupGen Updated"


def test_delete_fupgen(populated_session: Session):
    """Teste de remoção de um FupGen existente."""

    session = populated_session
    fupgen_db = session.query(FupGen).filter_by(id="id1").first()
    session.delete(fupgen_db)
    session.commit()

    # Verificando se foi removido
    fupgen_deleted = session.query(FupGen).filter_by(id="id1").first()
    assert fupgen_deleted is None
