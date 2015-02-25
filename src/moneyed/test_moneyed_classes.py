# -*- encoding: utf-8 -*-
#file test_moneyed_classes.py
from __future__ import division
from __future__ import unicode_literals

from copy import deepcopy
from decimal import Decimal
import warnings

import pytest  # Works with less code, more consistency than unittest.

from moneyed.classes import Currency, Money, MoneyComparisonError, CURRENCIES, DEFAULT_CURRENCY, USD, get_currency
from moneyed.localization import format_money


class TestCurrency:

    def setup_method(self, method):
        self.default_curr_code = 'XYZ'
        self.default_curr = CURRENCIES[self.default_curr_code]

    def test_init(self):
        usd_countries = CURRENCIES['USD'].countries
        US_dollars = Currency(
            code='USD',
            numeric='840',
            name='US Dollar',
            countries=['AMERICAN SAMOA',
                       'BRITISH INDIAN OCEAN TERRITORY',
                       'ECUADOR',
                       'GUAM',
                       'MARSHALL ISLANDS',
                       'MICRONESIA',
                       'NORTHERN MARIANA ISLANDS',
                       'PALAU',
                       'PUERTO RICO',
                       'TIMOR-LESTE',
                       'TURKS AND CAICOS ISLANDS',
                       'UNITED STATES',
                       'UNITED STATES MINOR OUTLYING ISLANDS',
                       'VIRGIN ISLANDS (BRITISH)',
                       'VIRGIN ISLANDS (U.S.)'])
        assert US_dollars.code == 'USD'
        assert US_dollars.countries == usd_countries
        assert US_dollars.name == 'US Dollar'
        assert US_dollars.numeric == '840'

    def test_repr(self):
        assert str(self.default_curr) == self.default_curr_code

    def test_compare(self):
        other = deepcopy(self.default_curr)
        # equality
        assert self.default_curr == CURRENCIES['XYZ']
        assert self.default_curr == other
        # non-equality
        other.code = 'USD'
        assert self.default_curr != other
        assert self.default_curr != CURRENCIES['USD']

    def test_fetching_currency_by_iso_code(self):
        assert get_currency('USD') == USD
        assert get_currency(iso='840') == USD
        assert get_currency(iso=840) == USD


class TestMoney:

    def setup_method(self, method):
        self.one_million_decimal = Decimal('1000000')
        self.USD = CURRENCIES['USD']
        self.one_million_bucks = Money(amount=self.one_million_decimal,
                                       currency=self.USD)

    def test_init(self):
        one_million_dollars = Money(amount=self.one_million_decimal,
                                    currency=self.USD)
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_string_currency_code(self):
        one_million_dollars = Money(amount=self.one_million_decimal,
                                    currency='usd')
        assert one_million_dollars.amount == self.one_million_decimal
        assert one_million_dollars.currency == self.USD

    def test_init_default_currency(self):
        one_million = self.one_million_decimal
        one_million_dollars = Money(amount=one_million)  # No currency given!
        assert one_million_dollars.amount == one_million
        assert one_million_dollars.currency == DEFAULT_CURRENCY

    def test_init_float(self):
        one_million_dollars = Money(amount=1000000.0)
        assert one_million_dollars.amount == self.one_million_decimal

    def test_repr(self):
        assert repr(self.one_million_bucks) == '1000000 USD'
        assert repr(Money(Decimal('2.000'), 'PLN')) == '2 PLN'
        m_1 = Money(Decimal('2.000'), 'PLN')
        m_2 = Money(Decimal('2.000000'), 'PLN')
        assert repr(m_1) == repr(m_2)

    def test_str(self):
        assert str(self.one_million_bucks) == 'US$1,000,000.00'

    def test_format_money(self):
        # Two decimal places by default
        assert format_money(self.one_million_bucks) == 'US$1,000,000.00'
        # No decimal point without fractional part
        assert format_money(self.one_million_bucks, decimal_places=0) == 'US$1,000,000'
        # locale == pl_PL
        one_million_pln = Money('1000000', 'PLN')
        # Two decimal places by default
        assert format_money(one_million_pln, locale='pl_PL') == '1 000 000,00 zł'
        assert format_money(self.one_million_bucks, locale='pl_PL') == '1 000 000,00 USD'
        # No decimal point without fractional part
        assert format_money(one_million_pln, locale='pl_PL',
                            decimal_places=0) == '1 000 000 zł'

    def test_add(self):
        assert (self.one_million_bucks + self.one_million_bucks
                == Money(amount='2000000', currency=self.USD))

    def test_add_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) + 123

    def test_sub(self):
        zeroed_test = self.one_million_bucks - self.one_million_bucks
        assert zeroed_test == Money(amount=0, currency=self.USD)

    def test_sub_non_money(self):
        with pytest.raises(TypeError):
            Money(1000) - 123

    def test_mul(self):
        x = Money(amount=111.33, currency=self.USD)
        assert 3 * x == Money(333.99, currency=self.USD)
        assert Money(333.99, currency=self.USD) == 3 * x

    def test_mul_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            Money(amount="10") * 1.2
            assert "Multiplying Money instances with floats is deprecated" in [w.message.args[0] for w in warning_list]

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            1.2 * Money(amount="10")
            assert "Multiplying Money instances with floats is deprecated" in [w.message.args[0] for w in warning_list]

    def test_mul_bad(self):
        with pytest.raises(TypeError):
            self.one_million_bucks * self.one_million_bucks

    def test_div(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=self.USD)
        assert x / y == Decimal(25)

    def test_div_mismatched_currencies(self):
        x = Money(amount=50, currency=self.USD)
        y = Money(amount=2, currency=CURRENCIES['CAD'])
        with pytest.raises(TypeError):
            assert x / y == Money(amount=25, currency=self.USD)

    def test_div_by_non_Money(self):
        x = Money(amount=50, currency=self.USD)
        y = 2
        assert x / y == Money(amount=25, currency=self.USD)

    def test_div_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            Money(amount="10") / 1.2
            assert "Dividing Money instances by floats is deprecated" in [w.message.args[0] for w in warning_list]

    def test_rmod(self):
        assert 1 % self.one_million_bucks == Money(amount=10000,
                                                   currency=self.USD)

    def test_rmod_bad(self):
        with pytest.raises(TypeError):
            assert (self.one_million_bucks % self.one_million_bucks
                    == 1)

    def test_rmod_float_warning(self):
        # This should be changed to TypeError exception after deprecation period is over.
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            2.0 % Money(amount="10")
            assert "Calculating percentages of Money instances using floats is deprecated" in [w.message.args[0] for w in warning_list]

    def test_convert_to_default(self):
        # Currency conversions are not implemented as of 2/2011; when
        # they are working, then convert_to_default and convert_to
        # will need to be tested.
        pass

    # Note: no tests for __eq__ as it's quite thoroughly covered in
    # the assert comparisons throughout these tests.

    def test_ne(self):
        x = Money(amount=1, currency=self.USD)
        assert self.one_million_bucks != x

    def test_equality_to_other_types(self):
        x = Money(amount=0, currency=self.USD)
        assert x != None
        assert x != {}

    def test_not_equal_to_decimal_types(self):
        assert self.one_million_bucks != self.one_million_decimal

    def test_lt(self):
        x = Money(amount=1, currency=self.USD)
        assert x < self.one_million_bucks

    def test_lt_mistyped(self):
        x = 1.0
        with pytest.raises(MoneyComparisonError):
            assert x < self.one_million_bucks

    def test_gt(self):
        x = Money(amount=1, currency=self.USD)
        assert self.one_million_bucks > x

    def test_gt_mistyped(self):
        x = 1.0
        with pytest.raises(MoneyComparisonError):
            assert self.one_million_bucks > x

    def test_abs(self):
        abs_money = Money(amount=1, currency=self.USD)
        x = Money(amount=-1, currency=self.USD)
        assert abs(x) == abs_money
        y = Money(amount=1, currency=self.USD)
        assert abs(x) == abs_money

    def test_sum(self):
        assert (sum([Money(amount=1, currency=self.USD),
                     Money(amount=2, currency=self.USD)]) ==
                Money(amount=3, currency=self.USD))

    def test_arithmetic_operations_return_real_subclass_instance(self):
        """
        Arithmetic operations on a subclass instance should return instances in the same subclass
        type.
        """

        extended_money = ExtendedMoney(amount=2, currency=self.USD)

        operated_money = +extended_money
        assert type(extended_money) == type(operated_money)
        operated_money = -extended_money
        assert type(extended_money) == type(operated_money)
        operated_money = ExtendedMoney(amount=1, currency=self.USD) + ExtendedMoney(amount=1, currency=self.USD)
        assert type(extended_money) == type(operated_money)
        operated_money = ExtendedMoney(amount=3, currency=self.USD) - Money(amount=1, currency=self.USD)
        assert type(extended_money) == type(operated_money)
        operated_money = (1 * extended_money)
        assert type(extended_money) == type(operated_money)
        operated_money = (extended_money / 1)
        assert type(extended_money) == type(operated_money)
        operated_money = abs(ExtendedMoney(amount=-2, currency=self.USD))
        assert type(extended_money) == type(operated_money)
        operated_money = (50 % ExtendedMoney(amount=4, currency=self.USD))
        assert type(extended_money) == type(operated_money)


class ExtendedMoney(Money):

    def do_my_behaviour(self):
        pass
