from datetime import datetime

from sqlalchemy.orm import Session

from infra.db.models.data import Data
from infra.db.models.fupgen import FupGen
from infra.db.models.msg import Message
from infra.db.models.recurrenceconfig import Recurrence


def test_create_fupgen(session: Session):
    recurrence = Recurrence(
        id="rec1",
        freq="daily",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        count=10,
        allow_infinite=True,
        is_exhausted=False,
    )
    session.add(recurrence)
    session.commit()

    message = Message(id="msg1", msg="Mensagem de teste")
    session.add(message)
    session.commit()

    data = Data(id="data1", data={"key": "value"})
    session.add(data)
    session.commit()

    fupgen = FupGen(
        id="fup1",
        hookid="hook1",
        ownerid="owner1",
        name="FupGen Test",
        description="Descrição do FupGen",
        default_cycle=5,
        recurrence_id=recurrence.id,
        message_id=message.id,
        data_id=data.id,
    )
    session.add(fupgen)
    session.commit()

    fupgen_db = session.query(FupGen).filter_by(id="fup1").first()
    assert fupgen_db is not None
    assert fupgen_db.name == "FupGen Test"
    assert fupgen_db.message.msg == "Mensagem de teste"
    assert fupgen_db.data.data == {"key": "value"}


def test_read_fupgen(session: Session):
    """Teste de leitura de um FupGen existente."""
    # Inserindo FupGen e dados necessários
    recurrence = Recurrence(
        id="rec2",
        freq="daily",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        is_exhausted=False,
    )
    session.add(recurrence)
    session.commit()

    message = Message(id="msg2", msg="Mensagem de teste")
    session.add(message)
    session.commit()

    data = Data(id="data2", data={"key": "value"})
    session.add(data)
    session.commit()

    fupgen = FupGen(
        id="fup2",
        hookid="hook1",
        ownerid="owner1",
        name="FupGen Test",
        description="Descrição do FupGen",
        default_cycle=5,
        recurrence_id=recurrence.id,
        message_id=message.id,
        data_id=data.id,
    )
    session.add(fupgen)
    session.commit()

    # Lendo o FupGen
    fupgen_db = session.query(FupGen).filter_by(id="fup2").first()

    # Verificando os dados
    assert fupgen_db is not None
    assert fupgen_db.name == "FupGen Test"
    assert fupgen_db.description == "Descrição do FupGen"


def test_update_fupgen(session: Session):
    """Teste de atualização de um FupGen existente."""
    # Inserindo FupGen e dados necessários
    recurrence = Recurrence(
        id="rec3",
        freq="daily",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        is_exhausted=False,
    )
    session.add(recurrence)
    session.commit()

    message = Message(id="msg3", msg="Mensagem de teste")
    session.add(message)
    session.commit()

    data = Data(id="data3", data={"key": "value"})
    session.add(data)
    session.commit()

    fupgen = FupGen(
        id="fup3",
        hookid="hook1",
        ownerid="owner1",
        name="FupGen Test",
        description="Descrição do FupGen",
        default_cycle=5,
        recurrence_id=recurrence.id,
        message_id=message.id,
        data_id=data.id,
    )
    session.add(fupgen)
    session.commit()

    # Atualizando o FupGen
    fupgen_db = session.query(FupGen).filter_by(id="fup3").first()
    fupgen_db.name = "FupGen Updated"
    session.commit()

    # Verificando se foi atualizado corretamente
    fupgen_updated = session.query(FupGen).filter_by(id="fup3").first()
    assert fupgen_updated.name == "FupGen Updated"


def test_delete_fupgen(session: Session):
    """Teste de remoção de um FupGen existente."""
    # Inserindo FupGen e dados necessários
    recurrence = Recurrence(
        id="rec4",
        freq="daily",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        is_exhausted=False,
    )
    session.add(recurrence)
    session.commit()

    message = Message(id="msg4", msg="Mensagem de teste")
    session.add(message)
    session.commit()

    data = Data(id="data4", data={"key": "value"})
    session.add(data)
    session.commit()

    fupgen = FupGen(
        id="fup4",
        hookid="hook1",
        ownerid="owner1",
        name="FupGen Test",
        description="Descrição do FupGen",
        default_cycle=5,
        recurrence_id=recurrence.id,
        message_id=message.id,
        data_id=data.id,
    )
    session.add(fupgen)
    session.commit()

    # Deletando o FupGen
    fupgen_db = session.query(FupGen).filter_by(id="fup4").first()
    session.delete(fupgen_db)
    session.commit()

    # Verificando se foi removido
    fupgen_deleted = session.query(FupGen).filter_by(id="fup4").first()
    assert fupgen_deleted is None
