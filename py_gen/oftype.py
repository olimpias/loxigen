# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

import of_g
import loxi_utils.loxi_utils as utils
import loxi_front_end.type_maps
import unittest

class OFType(object):
    """
    Encapsulates knowledge about the OpenFlow type system.
    """

    version = None
    base = None
    is_array = False
    array_length = None

    def __init__(self, string, version):
        self.version = version
        self.array_length, self.base = utils.type_dec_to_count_base(string)
        self.is_array = self.array_length != 1

    def gen_init_expr(self):
        if utils.class_is_list(self.base):
            v = "[]"
        elif self.base.find("uint") == 0 or self.base in ["char", "of_port_no_t"]:
            v = "0"
        elif self.base == 'of_mac_addr_t':
            v = '[0,0,0,0,0,0]'
        elif self.base == 'of_ipv6_t':
            v = repr('\x00' * 16)
        elif self.base == 'of_wc_bmap_t':
            v = 'const.OFPFW_ALL'
        elif self.base in ['of_octets_t', 'of_port_name_t', 'of_table_name_t',
                           'of_desc_str_t', 'of_serial_num_t']:
            v = '""'
        elif self.base == 'of_match_t':
            v = 'common.match()'
        elif self.base == 'of_port_desc_t':
            v = 'common.port_desc()'
        else:
            v = "None"

        if self.is_array:
            return "[" + ','.join([v] * self.array_length) + "]"
        else:
            return v

    def gen_pack_expr(self, expr_expr):
        pack_fmt = self._pack_fmt()
        if pack_fmt and not self.is_array:
            return 'struct.pack("!%s", %s)' % (pack_fmt, expr_expr)
        elif pack_fmt and self.is_array:
            return 'struct.pack("!%s%s", *%s)' % (self.array_length, pack_fmt, expr_expr)
        elif self.base == 'of_octets_t':
            return expr_expr
        elif utils.class_is_list(self.base):
            return '"".join([x.pack() for x in %s])' % expr_expr
        elif self.base == 'of_mac_addr_t':
            return 'struct.pack("!6B", *%s)' % expr_expr
        elif self.base == 'of_ipv6_t':
            return 'struct.pack("!16s", %s)' % expr_expr
        elif self.base in ['of_match_t', 'of_port_desc_t']:
            return '%s.pack()' % expr_expr
        elif self.base == 'of_port_name_t':
            return self._gen_string_pack_expr(16, expr_expr)
        elif self.base == 'of_table_name_t' or self.base == 'of_serial_num_t':
            return self._gen_string_pack_expr(32, expr_expr)
        elif self.base == 'of_desc_str_t':
            return self._gen_string_pack_expr(256, expr_expr)
        else:
            return "loxi.unimplemented('pack %s')" % self.base

    def _gen_string_pack_expr(self, length, expr_expr):
        return 'struct.pack("!%ds", %s)' % (length, expr_expr)

    def gen_unpack_expr(self, reader_expr):
        pack_fmt = self._pack_fmt()
        if pack_fmt and not self.is_array:
            return "%s.read('!%s')[0]" % (reader_expr, pack_fmt)
        elif pack_fmt and self.is_array:
            return "list(%s.read('!%d%s'))" % (self.array_length, pack_fmt)
        elif self.base == 'of_octets_t':
            return "str(%s.read_all())" % (reader_expr)
        elif self.base == 'of_mac_addr_t':
            return "list(%s.read('!6B'))" % (reader_expr)
        elif self.base == 'of_ipv6_t':
            return "%s.read('!16s')[0]" % (reader_expr)
        elif self.base == 'of_match_t':
            return 'common.match.unpack(%s)' % (reader_expr)
        elif self.base == 'of_port_desc_t':
            return 'common.port_desc.unpack(%s)' % (reader_expr)
        elif self.base == 'of_list_action_t':
            return 'action.unpack_list(%s)' % (reader_expr)
        elif self.base == 'of_list_flow_stats_entry_t':
            return 'common.unpack_list_flow_stats_entry(%s)' % (reader_expr)
        elif self.base == 'of_list_queue_prop_t':
            return 'common.unpack_list_queue_prop(%s)' % (reader_expr)
        elif self.base == 'of_list_packet_queue_t':
            return 'common.unpack_list_packet_queue(%s)' % (reader_expr)
        elif self.base == 'of_list_hello_elem_t':
            return 'common.unpack_list_hello_elem(%s)' % (reader_expr)
        elif self.base == 'of_list_oxm_t':
            # HACK need the match_v3 length field
            return 'oxm.unpack_list(%s.slice(_length-4))' % (reader_expr)
        elif self.base == 'of_list_bucket_t':
            return 'common.unpack_list_bucket(%s)' % (reader_expr)
        elif self.base == 'of_port_name_t':
            return self._gen_string_unpack_expr(reader_expr, 16)
        elif self.base == 'of_table_name_t' or self.base == 'of_serial_num_t':
            return self._gen_string_unpack_expr(reader_expr, 32)
        elif self.base == 'of_desc_str_t':
            return self._gen_string_unpack_expr(reader_expr, 256)
        elif utils.class_is_list(self.base):
            element_cls = utils.list_to_entry_type(self.base)[:-2]
            if ((element_cls, self.version) in of_g.is_fixed_length) \
               and not element_cls in loxi_front_end.type_maps.inheritance_map:
                klass_name = self.base[8:-2]
                element_size, = of_g.base_length[(element_cls, self.version)],
                return 'loxi.generic_util.unpack_list(%s, common.%s.unpack)' % (reader_expr, klass_name)
            else:
                return "loxi.unimplemented('unpack list %s')" % self.base
        else:
            return "loxi.unimplemented('unpack %s')" % self.base

    def _gen_string_unpack_expr(self, reader_expr, length):
        return '%s.read("!%ds")[0].rstrip("\\x00")' % (reader_expr, length)

    def _pack_fmt(self):
        if self.base == "char":
            return "B"
        if self.base == "uint8_t":
            return "B"
        if self.base == "uint16_t":
            return "H"
        if self.base == "uint32_t":
            return "L"
        if self.base == "uint64_t":
            return "Q"
        if self.base == "of_port_no_t":
            if self.version == of_g.VERSION_1_0:
                return "H"
            else:
                return "L"
        if self.base == "of_fm_cmd_t":
            if self.version == of_g.VERSION_1_0:
                return "H"
            else:
                return "B"
        if self.base in ["of_wc_bmap_t", "of_match_bmap_t"]:
            if self.version in [of_g.VERSION_1_0, of_g.VERSION_1_1]:
                return "L"
            else:
                return "Q"
        return None

class TestOFType(unittest.TestCase):
    def test_init(self):
        from oftype import OFType
        self.assertEquals("None", OFType("of_list_action_t", 1).gen_init_expr())
        self.assertEquals("[0,0,0]", OFType("uint32_t[3]", 1).gen_init_expr())

    def test_pack(self):
        self.assertEquals('struct.pack("!16s", "foo")', OFType("of_port_name_t", 1).gen_pack_expr('"foo"'))

    def test_unpack(self):
        self.assertEquals('str(buffer(buf, 8, 16)).rstrip("\\x00")', OFType("of_port_name_t", 1).gen_unpack_expr('buf', 8))

if __name__ == '__main__':
    unittest.main()
