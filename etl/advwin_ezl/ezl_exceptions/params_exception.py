#!/usr/bin/python
# -*- encoding: utf-8 -*-


class ParamsException(Exception):
    def __init__(self):
        msg = """
        Nao foi informado a senha para execucao do script conforme o exemplo a seguir!\n
        Ex: python3.5 luigi_jobs.py -p=SENHA DO USUARIO QUE ESTA EXECUTANDO O'SCRIPT'
        """
        Exception.__init__(self, msg)

