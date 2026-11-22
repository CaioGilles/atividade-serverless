import base64
import json

import pytest

from hello_world import app


@pytest.fixture()
def apigw_event():
    """Generates API GW Event for Rota Vital /guias"""

    return {
        "body": json.dumps(
            {
                "requisicaoId": "R-001",
                "hospital": "H-Recife",
                "bolsas": ["O-NEG-0142"],
            }
        ),
        "resource": "/{proxy+}",
        "path": "/guias",
        "httpMethod": "POST",
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "POST",
            "stage": "prod",
        },
    }


def test_lambda_handler_sucesso(apigw_event):
    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 201
    assert data["guia"] == "G-R-001"
    assert data["hospital"] == "H-Recife"
    assert data["bolsas"] == ["O-NEG-0142"]
    assert data["invocacaoNesteAmbiente"] >= 1


def test_lambda_handler_sem_requisicao_id():
    event = {"body": json.dumps({"hospital": "H-Recife"})}
    ret = app.lambda_handler(event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 400
    assert data["erro"] == "requisicaoId obrigatório"


def test_lambda_handler_body_base64():
    payload = json.dumps({"requisicaoId": "R-009", "hospital": "H-Olinda"})
    event = {
        "body": base64.b64encode(payload.encode("utf-8")).decode("utf-8"),
        "isBase64Encoded": True,
    }
    ret = app.lambda_handler(event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 201
    assert data["guia"] == "G-R-009"
