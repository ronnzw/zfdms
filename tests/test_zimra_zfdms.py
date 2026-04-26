#!/usr/bin/env python
import pytest
import requests

"""Tests for `zimra_zfdms` package."""

from zfdms import client


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    pass
    # import requests
    # return requests.get('https://github.com/audreyfeldroy/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    pass
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
