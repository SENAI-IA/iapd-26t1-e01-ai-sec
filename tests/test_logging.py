import logging

from app.logging_ import mask_pan


def test_r10_pan_completo_nao_aparece_no_log(caplog):
    pan = "4111 1111 1111 1111"
    logger = logging.getLogger("app.test_r10")

    with caplog.at_level(logging.INFO, logger=logger.name):
        logger.info("Pagamento com cartão %s", mask_pan(pan))

    assert "4111111111111111" not in caplog.text
    assert "1111" in caplog.text
    assert "************1111" in caplog.text
