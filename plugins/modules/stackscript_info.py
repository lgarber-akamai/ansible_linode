#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module allows users to retrieve information about a Linode StackScript."""

from __future__ import absolute_import, division, print_function

import ansible_collections.linode.cloud.plugins.module_utils.doc_fragments.stackscript as docs_parent
import ansible_collections.linode.cloud.plugins.module_utils.doc_fragments.stackscript_info as docs
from ansible_collections.linode.cloud.plugins.module_utils.linode_common_info import (
    InfoModuleAttr,
    InfoModuleBase,
    InfoModuleResponse,
)
from ansible_specdoc.objects import FieldType
from linode_api4 import StackScript


class Module(InfoModuleBase):
    """Module for getting info about a Linode StackScript"""

    examples = docs.specdoc_examples

    primary_response = InfoModuleResponse(
        field="stackscript",
        field_type=FieldType.dict,
        display_name="StackScript",
        samples=docs_parent.result_stackscript_samples,
    )

    attributes = {
        "id": InfoModuleAttr(
            display_name="ID",
            type=FieldType.integer,
            get=lambda client, params: client.load(
                StackScript, params.get("id")
            )._raw_json,
        ),
        "label": InfoModuleAttr(
            display_name="label",
            type=FieldType.string,
            get=lambda client, params: client.linode.stackscripts(
                StackScript.label == params.get("label")
            )[0]._raw_json,
        ),
    }


SPECDOC_META = Module.spec

if __name__ == "__main__":
    Module()
