# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-08 17:44
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0075_auto_20180418_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('create_date',
                 models.DateTimeField(
                     auto_now_add=True, verbose_name='Criado em')),
                ('alter_date',
                 models.DateTimeField(
                     auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('name', models.CharField(max_length=255,
                                          verbose_name='Nome')),
                ('description',
                 models.TextField(
                     blank=True, null=True, verbose_name='Descrição')),
                ('month_value_currency',
                 djmoney.models.fields.CurrencyField(
                     choices=[
                         ('XUA', 'ADB Unit of Account'), ('AFN', 'Afghani'),
                         ('DZD', 'Algerian Dinar'), ('ARS', 'Argentine Peso'),
                         ('AMD', 'Armenian Dram'), ('AWG', 'Aruban Guilder'),
                         ('AUD', 'Australian Dollar'),
                         ('AZN', 'Azerbaijanian Manat'),
                         ('BSD', 'Bahamian Dollar'), ('BHD', 'Bahraini Dinar'),
                         ('THB', 'Baht'), ('PAB', 'Balboa'),
                         ('BBD', 'Barbados Dollar'),
                         ('BYN', 'Belarussian Ruble'),
                         ('BYR', 'Belarussian Ruble'), ('BZD',
                                                        'Belize Dollar'),
                         ('BMD',
                          'Bermudian Dollar (customarily known as Bermuda Dollar)'
                          ), ('BTN', 'Bhutanese ngultrum'),
                         ('VEF', 'Bolivar Fuerte'), ('BOB', 'Boliviano'),
                         ('XBA',
                          'Bond Markets Units European Composite Unit (EURCO)'
                          ), ('BRL', 'Brazilian Real'), ('BND',
                                                         'Brunei Dollar'),
                         ('BGN', 'Bulgarian Lev'), ('BIF', 'Burundi Franc'),
                         ('XOF', 'CFA Franc BCEAO'), ('XAF', 'CFA franc BEAC'),
                         ('XPF', 'CFP Franc'), ('CAD', 'Canadian Dollar'),
                         ('CVE', 'Cape Verde Escudo'),
                         ('KYD', 'Cayman Islands Dollar'),
                         ('CLP', 'Chilean peso'),
                         ('XTS',
                          'Codes specifically reserved for testing purposes'),
                         ('COP', 'Colombian peso'), ('KMF', 'Comoro Franc'),
                         ('CDF', 'Congolese franc'),
                         ('BAM', 'Convertible Marks'), ('NIO', 'Cordoba Oro'),
                         ('CRC', 'Costa Rican Colon'), ('HRK',
                                                        'Croatian Kuna'),
                         ('CUP', 'Cuban Peso'),
                         ('CUC', 'Cuban convertible peso'),
                         ('CZK', 'Czech Koruna'), ('GMD', 'Dalasi'),
                         ('DKK', 'Danish Krone'), ('MKD', 'Denar'),
                         ('DJF', 'Djibouti Franc'), ('STD', 'Dobra'),
                         ('DOP', 'Dominican Peso'), ('VND', 'Dong'),
                         ('XCD', 'East Caribbean Dollar'),
                         ('EGP', 'Egyptian Pound'), ('SVC',
                                                     'El Salvador Colon'),
                         ('ETB', 'Ethiopian Birr'), ('EUR', 'Euro'),
                         ('XBB', 'European Monetary Unit (E.M.U.-6)'),
                         ('XBD', 'European Unit of Account 17(E.U.A.-17)'),
                         ('XBC', 'European Unit of Account 9(E.U.A.-9)'),
                         ('FKP', 'Falkland Islands Pound'),
                         ('FJD', 'Fiji Dollar'), ('HUF', 'Forint'),
                         ('GHS', 'Ghana Cedi'), ('GIP', 'Gibraltar Pound'),
                         ('XAU', 'Gold'), ('XFO', 'Gold-Franc'),
                         ('PYG', 'Guarani'), ('GNF', 'Guinea Franc'),
                         ('GYD', 'Guyana Dollar'), ('HTG', 'Haitian gourde'),
                         ('HKD', 'Hong Kong Dollar'), ('UAH', 'Hryvnia'),
                         ('ISK', 'Iceland Krona'), ('INR', 'Indian Rupee'),
                         ('IRR', 'Iranian Rial'), ('IQD', 'Iraqi Dinar'),
                         ('IMP', 'Isle of Man Pound'),
                         ('JMD', 'Jamaican Dollar'), ('JOD',
                                                      'Jordanian Dinar'),
                         ('KES', 'Kenyan Shilling'), ('PGK', 'Kina'),
                         ('LAK', 'Kip'), ('KWD', 'Kuwaiti Dinar'),
                         ('AOA', 'Kwanza'), ('MMK', 'Kyat'), ('GEL', 'Lari'),
                         ('LVL', 'Latvian Lats'), ('LBP', 'Lebanese Pound'),
                         ('ALL', 'Lek'), ('HNL', 'Lempira'), ('SLL', 'Leone'),
                         ('LSL', 'Lesotho loti'), ('LRD', 'Liberian Dollar'),
                         ('LYD', 'Libyan Dinar'), ('SZL', 'Lilangeni'),
                         ('LTL', 'Lithuanian Litas'), ('MGA',
                                                       'Malagasy Ariary'),
                         ('MWK', 'Malawian Kwacha'),
                         ('MYR', 'Malaysian Ringgit'), ('TMM', 'Manat'),
                         ('MUR', 'Mauritius Rupee'), ('MZN', 'Metical'),
                         ('MXV', 'Mexican Unidad de Inversion (UDI)'),
                         ('MXN', 'Mexican peso'), ('MDL', 'Moldovan Leu'),
                         ('MAD', 'Moroccan Dirham'), ('BOV', 'Mvdol'),
                         ('NGN', 'Naira'), ('ERN', 'Nakfa'),
                         ('NAD', 'Namibian Dollar'), ('NPR', 'Nepalese Rupee'),
                         ('ANG', 'Netherlands Antillian Guilder'),
                         ('ILS', 'New Israeli Sheqel'), ('RON', 'New Leu'),
                         ('TWD', 'New Taiwan Dollar'),
                         ('NZD',
                          'New Zealand Dollar'), ('KPW', 'North Korean Won'),
                         ('NOK', 'Norwegian Krone'), ('PEN', 'Nuevo Sol'),
                         ('MRO', 'Ouguiya'), ('TOP', 'Paanga'),
                         ('PKR', 'Pakistan Rupee'), ('XPD', 'Palladium'),
                         ('MOP', 'Pataca'), ('PHP', 'Philippine Peso'),
                         ('XPT', 'Platinum'), ('GBP', 'Pound Sterling'),
                         ('BWP', 'Pula'), ('QAR', 'Qatari Rial'),
                         ('GTQ', 'Quetzal'), ('ZAR', 'Rand'),
                         ('OMR', 'Rial Omani'), ('KHR', 'Riel'),
                         ('MVR', 'Rufiyaa'), ('IDR', 'Rupiah'),
                         ('RUB', 'Russian Ruble'), ('RWF', 'Rwanda Franc'),
                         ('XDR', 'SDR'), ('SHP', 'Saint Helena Pound'),
                         ('SAR', 'Saudi Riyal'), ('RSD', 'Serbian Dinar'),
                         ('SCR', 'Seychelles Rupee'), ('XAG', 'Silver'),
                         ('SGD', 'Singapore Dollar'),
                         ('SBD', 'Solomon Islands Dollar'), ('KGS', 'Som'),
                         ('SOS', 'Somali Shilling'), ('TJS', 'Somoni'),
                         ('SSP', 'South Sudanese Pound'),
                         ('LKR', 'Sri Lanka Rupee'), ('XSU', 'Sucre'),
                         ('SDG', 'Sudanese Pound'), ('SRD', 'Surinam Dollar'),
                         ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'),
                         ('SYP', 'Syrian Pound'), ('BDT', 'Taka'),
                         ('WST', 'Tala'), ('TZS', 'Tanzanian Shilling'),
                         ('KZT', 'Tenge'),
                         ('XXX',
                          'The codes assigned for transactions where no currency is involved'
                          ), ('TTD', 'Trinidad and Tobago Dollar'),
                         ('MNT', 'Tugrik'), ('TND', 'Tunisian Dinar'),
                         ('TRY', 'Turkish Lira'),
                         ('TMT', 'Turkmenistan New Manat'),
                         ('TVD', 'Tuvalu dollar'), ('AED', 'UAE Dirham'),
                         ('XFU', 'UIC-Franc'), ('USD', 'US Dollar'),
                         ('USN', 'US Dollar (Next day)'),
                         ('UGX', 'Uganda Shilling'),
                         ('CLF', 'Unidad de Fomento'),
                         ('COU', 'Unidad de Valor Real'),
                         ('UYI',
                          'Uruguay Peso en Unidades Indexadas (URUIURUI)'),
                         ('UYU', 'Uruguayan peso'), ('UZS', 'Uzbekistan Sum'),
                         ('VUV', 'Vatu'), ('CHE', 'WIR Euro'),
                         ('CHW', 'WIR Franc'), ('KRW', 'Won'),
                         ('YER', 'Yemeni Rial'), ('JPY', 'Yen'),
                         ('CNY', 'Yuan Renminbi'), ('ZMK', 'Zambian Kwacha'),
                         ('ZMW', 'Zambian Kwacha'),
                         ('ZWD', 'Zimbabwe Dollar A/06'),
                         ('ZWN', 'Zimbabwe dollar A/08'),
                         ('ZWL', 'Zimbabwe dollar A/09'), ('PLN', 'Zloty')
                     ],
                     default='BRL',
                     editable=False,
                     max_length=3)),
                ('month_value',
                 djmoney.models.fields.MoneyField(
                     decimal_places=2,
                     default=Decimal('0.0'),
                     default_currency='BRL',
                     max_digits=10,
                     verbose_name='Valor mensal')),
                ('task_limit',
                 models.IntegerField(
                     blank=True, null=True, verbose_name='Limite mensal')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='plan_alter_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Alterado por')),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='plan_create_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Plano',
                'verbose_name_plural': 'Planos',
                'ordering': ['month_value'],
            },
        ),
        migrations.CreateModel(
            name='PlanOffice',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('create_date',
                 models.DateTimeField(
                     auto_now_add=True, verbose_name='Criado em')),
                ('alter_date',
                 models.DateTimeField(
                     auto_now=True, null=True, verbose_name='Atualizado em')),
                ('is_active',
                 models.BooleanField(default=True, verbose_name='Ativo')),
                ('subscription_date',
                 models.DateTimeField(
                     auto_now_add=True, verbose_name='Data de inscrição')),
                ('cancelation_date',
                 models.DateTimeField(
                     blank=True,
                     null=True,
                     verbose_name='Data de cancelamento')),
                ('month_value_currency',
                 djmoney.models.fields.CurrencyField(
                     choices=[
                         ('XUA', 'ADB Unit of Account'), ('AFN', 'Afghani'),
                         ('DZD', 'Algerian Dinar'), ('ARS', 'Argentine Peso'),
                         ('AMD', 'Armenian Dram'), ('AWG', 'Aruban Guilder'),
                         ('AUD', 'Australian Dollar'),
                         ('AZN', 'Azerbaijanian Manat'),
                         ('BSD', 'Bahamian Dollar'), ('BHD', 'Bahraini Dinar'),
                         ('THB', 'Baht'), ('PAB', 'Balboa'),
                         ('BBD', 'Barbados Dollar'),
                         ('BYN', 'Belarussian Ruble'),
                         ('BYR', 'Belarussian Ruble'), ('BZD',
                                                        'Belize Dollar'),
                         ('BMD',
                          'Bermudian Dollar (customarily known as Bermuda Dollar)'
                          ), ('BTN', 'Bhutanese ngultrum'),
                         ('VEF', 'Bolivar Fuerte'), ('BOB', 'Boliviano'),
                         ('XBA',
                          'Bond Markets Units European Composite Unit (EURCO)'
                          ), ('BRL', 'Brazilian Real'), ('BND',
                                                         'Brunei Dollar'),
                         ('BGN', 'Bulgarian Lev'), ('BIF', 'Burundi Franc'),
                         ('XOF', 'CFA Franc BCEAO'), ('XAF', 'CFA franc BEAC'),
                         ('XPF', 'CFP Franc'), ('CAD', 'Canadian Dollar'),
                         ('CVE', 'Cape Verde Escudo'),
                         ('KYD', 'Cayman Islands Dollar'),
                         ('CLP', 'Chilean peso'),
                         ('XTS',
                          'Codes specifically reserved for testing purposes'),
                         ('COP', 'Colombian peso'), ('KMF', 'Comoro Franc'),
                         ('CDF', 'Congolese franc'),
                         ('BAM', 'Convertible Marks'), ('NIO', 'Cordoba Oro'),
                         ('CRC', 'Costa Rican Colon'), ('HRK',
                                                        'Croatian Kuna'),
                         ('CUP', 'Cuban Peso'),
                         ('CUC', 'Cuban convertible peso'),
                         ('CZK', 'Czech Koruna'), ('GMD', 'Dalasi'),
                         ('DKK', 'Danish Krone'), ('MKD', 'Denar'),
                         ('DJF', 'Djibouti Franc'), ('STD', 'Dobra'),
                         ('DOP', 'Dominican Peso'), ('VND', 'Dong'),
                         ('XCD', 'East Caribbean Dollar'),
                         ('EGP', 'Egyptian Pound'), ('SVC',
                                                     'El Salvador Colon'),
                         ('ETB', 'Ethiopian Birr'), ('EUR', 'Euro'),
                         ('XBB', 'European Monetary Unit (E.M.U.-6)'),
                         ('XBD', 'European Unit of Account 17(E.U.A.-17)'),
                         ('XBC', 'European Unit of Account 9(E.U.A.-9)'),
                         ('FKP', 'Falkland Islands Pound'),
                         ('FJD', 'Fiji Dollar'), ('HUF', 'Forint'),
                         ('GHS', 'Ghana Cedi'), ('GIP', 'Gibraltar Pound'),
                         ('XAU', 'Gold'), ('XFO', 'Gold-Franc'),
                         ('PYG', 'Guarani'), ('GNF', 'Guinea Franc'),
                         ('GYD', 'Guyana Dollar'), ('HTG', 'Haitian gourde'),
                         ('HKD', 'Hong Kong Dollar'), ('UAH', 'Hryvnia'),
                         ('ISK', 'Iceland Krona'), ('INR', 'Indian Rupee'),
                         ('IRR', 'Iranian Rial'), ('IQD', 'Iraqi Dinar'),
                         ('IMP', 'Isle of Man Pound'),
                         ('JMD', 'Jamaican Dollar'), ('JOD',
                                                      'Jordanian Dinar'),
                         ('KES', 'Kenyan Shilling'), ('PGK', 'Kina'),
                         ('LAK', 'Kip'), ('KWD', 'Kuwaiti Dinar'),
                         ('AOA', 'Kwanza'), ('MMK', 'Kyat'), ('GEL', 'Lari'),
                         ('LVL', 'Latvian Lats'), ('LBP', 'Lebanese Pound'),
                         ('ALL', 'Lek'), ('HNL', 'Lempira'), ('SLL', 'Leone'),
                         ('LSL', 'Lesotho loti'), ('LRD', 'Liberian Dollar'),
                         ('LYD', 'Libyan Dinar'), ('SZL', 'Lilangeni'),
                         ('LTL', 'Lithuanian Litas'), ('MGA',
                                                       'Malagasy Ariary'),
                         ('MWK', 'Malawian Kwacha'),
                         ('MYR', 'Malaysian Ringgit'), ('TMM', 'Manat'),
                         ('MUR', 'Mauritius Rupee'), ('MZN', 'Metical'),
                         ('MXV', 'Mexican Unidad de Inversion (UDI)'),
                         ('MXN', 'Mexican peso'), ('MDL', 'Moldovan Leu'),
                         ('MAD', 'Moroccan Dirham'), ('BOV', 'Mvdol'),
                         ('NGN', 'Naira'), ('ERN', 'Nakfa'),
                         ('NAD', 'Namibian Dollar'), ('NPR', 'Nepalese Rupee'),
                         ('ANG', 'Netherlands Antillian Guilder'),
                         ('ILS', 'New Israeli Sheqel'), ('RON', 'New Leu'),
                         ('TWD', 'New Taiwan Dollar'),
                         ('NZD',
                          'New Zealand Dollar'), ('KPW', 'North Korean Won'),
                         ('NOK', 'Norwegian Krone'), ('PEN', 'Nuevo Sol'),
                         ('MRO', 'Ouguiya'), ('TOP', 'Paanga'),
                         ('PKR', 'Pakistan Rupee'), ('XPD', 'Palladium'),
                         ('MOP', 'Pataca'), ('PHP', 'Philippine Peso'),
                         ('XPT', 'Platinum'), ('GBP', 'Pound Sterling'),
                         ('BWP', 'Pula'), ('QAR', 'Qatari Rial'),
                         ('GTQ', 'Quetzal'), ('ZAR', 'Rand'),
                         ('OMR', 'Rial Omani'), ('KHR', 'Riel'),
                         ('MVR', 'Rufiyaa'), ('IDR', 'Rupiah'),
                         ('RUB', 'Russian Ruble'), ('RWF', 'Rwanda Franc'),
                         ('XDR', 'SDR'), ('SHP', 'Saint Helena Pound'),
                         ('SAR', 'Saudi Riyal'), ('RSD', 'Serbian Dinar'),
                         ('SCR', 'Seychelles Rupee'), ('XAG', 'Silver'),
                         ('SGD', 'Singapore Dollar'),
                         ('SBD', 'Solomon Islands Dollar'), ('KGS', 'Som'),
                         ('SOS', 'Somali Shilling'), ('TJS', 'Somoni'),
                         ('SSP', 'South Sudanese Pound'),
                         ('LKR', 'Sri Lanka Rupee'), ('XSU', 'Sucre'),
                         ('SDG', 'Sudanese Pound'), ('SRD', 'Surinam Dollar'),
                         ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'),
                         ('SYP', 'Syrian Pound'), ('BDT', 'Taka'),
                         ('WST', 'Tala'), ('TZS', 'Tanzanian Shilling'),
                         ('KZT', 'Tenge'),
                         ('XXX',
                          'The codes assigned for transactions where no currency is involved'
                          ), ('TTD', 'Trinidad and Tobago Dollar'),
                         ('MNT', 'Tugrik'), ('TND', 'Tunisian Dinar'),
                         ('TRY', 'Turkish Lira'),
                         ('TMT', 'Turkmenistan New Manat'),
                         ('TVD', 'Tuvalu dollar'), ('AED', 'UAE Dirham'),
                         ('XFU', 'UIC-Franc'), ('USD', 'US Dollar'),
                         ('USN', 'US Dollar (Next day)'),
                         ('UGX', 'Uganda Shilling'),
                         ('CLF', 'Unidad de Fomento'),
                         ('COU', 'Unidad de Valor Real'),
                         ('UYI',
                          'Uruguay Peso en Unidades Indexadas (URUIURUI)'),
                         ('UYU', 'Uruguayan peso'), ('UZS', 'Uzbekistan Sum'),
                         ('VUV', 'Vatu'), ('CHE', 'WIR Euro'),
                         ('CHW', 'WIR Franc'), ('KRW', 'Won'),
                         ('YER', 'Yemeni Rial'), ('JPY', 'Yen'),
                         ('CNY', 'Yuan Renminbi'), ('ZMK', 'Zambian Kwacha'),
                         ('ZMW', 'Zambian Kwacha'),
                         ('ZWD', 'Zimbabwe Dollar A/06'),
                         ('ZWN', 'Zimbabwe dollar A/08'),
                         ('ZWL', 'Zimbabwe dollar A/09'), ('PLN', 'Zloty')
                     ],
                     default='BRL',
                     editable=False,
                     max_length=3)),
                ('month_value',
                 djmoney.models.fields.MoneyField(
                     decimal_places=2,
                     default=Decimal('0.0'),
                     default_currency='BRL',
                     max_digits=10,
                     verbose_name='Valor mensal')),
                ('task_limit',
                 models.IntegerField(
                     blank=True, null=True, verbose_name='Limite mensal')),
                ('alter_user',
                 models.ForeignKey(
                     blank=True,
                     null=True,
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='planoffice_alter_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Alterado por')),
                ('create_user',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     related_name='planoffice_create_user',
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='Criado por')),
                ('office',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     to='core.Office')),
                ('plan',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.PROTECT,
                     to='billing.Plan')),
            ],
            options={
                'ordering': ['office'],
            },
        ),
    ]
