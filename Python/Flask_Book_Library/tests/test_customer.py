import unittest
from project.customers.models import Customer


class TestCustomerModel(unittest.TestCase):


    def test_correct_input(self):
        valid_customers = [
            ("Jan Kowalski", "Warszawa", 30, "90010112345", "Marszalkowska 10", "12A"),
            ("Anna Nowak", "Krakow", 18, "08210154321", "Florianska 5", "1"),
            ("A" * 64, "B" * 64, 99, "85050512345", "C" * 128, "D" * 10),
        ]

        for name, city, age, pesel, street, app_no in valid_customers:
            with self.subTest(name=name):
                customer = Customer(
                    name=name,
                    city=city,
                    age=age,
                    pesel=pesel,
                    street=street,
                    appNo=app_no,
                )
                self.assertEqual(customer.name, name)
                self.assertEqual(customer.city, city)
                self.assertEqual(customer.age, age)
                self.assertEqual(customer.pesel, pesel)
                self.assertEqual(customer.street, street)
                self.assertEqual(customer.appNo, app_no)


    def test_incorrect_input(self):
        invalid_strings = [
            None,
            "",
            "null",
            "nil",
            "0",
            "\t",
            "\n",
            "   ",
            "=0@$*^%;<!->.:\\0&#\"",
            "©@£$§][]´Ωé®†μϋιωπ΄~,ν<>'',..",
        ]

        for value in invalid_strings:
            with self.subTest(value=repr(value)):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=value,
                        city=value,
                        age=30,
                        pesel=value,
                        street=value,
                        appNo=value,
                    )

    def test_incorrect_input_age_and_pesel_format(self):
        invalid_cases = [
            ("Jan Kowalski", "Warszawa", -5, "90010112345", "Prosta 1", "1"),
            ("Jan Kowalski", "Warszawa", "trzydziesci", "90010112345", "Prosta 1", "1"),
            ("Jan Kowalski", "Warszawa", None, "90010112345", "Prosta 1", "1"),
            ("Jan Kowalski", "Warszawa", 30, "123-ABC-789", "Prosta 1", "1"),
        ]

        for name, city, age, pesel, street, app_no in invalid_cases:
            with self.subTest(age=age, pesel=pesel):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=name,
                        city=city,
                        age=age,
                        pesel=pesel,
                        street=street,
                        appNo=app_no,
                    )


    def test_incorrect_input_xss(self):
        xss_payloads = [
            "\"-prompt(8)-\"",
            "'-prompt(8)-'",
            "<img/src/onerror=prompt(8)>",
            "<script\\x20type=\"text/javascript\">javascript:alert(1);</script>",
            "\"><\\x3Cscript>javascript:alert(1)</script>",
            "<script src=1 href=1 onerror=\"javascript:alert(1)\"></script>",
        ]

        for payload in xss_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=payload,
                        city="Warszawa",
                        age=30,
                        pesel="90010112345",
                        street=payload,
                        appNo="10",
                    )


    def test_incorrect_input_sqli(self):
        sqli_payloads = [
            "' or #",
            "\" OR 1=1",
            "' UNION SELECT '2",
            "1' ORDER BY 1--+",
            "' UNION SELECT sum(columnname) from tablename",
            ", (select * from (select(sleep(10)))a)",
        ]

        for payload in sqli_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=payload,
                        city=payload,
                        age=30,
                        pesel="90010112345",
                        street="Prosta 1",
                        appNo="10",
                    )


    def test_incorrect_input_boundary(self):
        # W models.py: name=String(64), city=String(64), street=String(128), appNo=String(10)
        # Sprawdzamy wartości dokładnie o 1 znak / jednostkę poza granicą poprawności
        boundary_cases = [
            # name ma 65 znaków (limit kolumny to 64)
            ("X" * 65, "Warszawa", 30, "90010112345", "Prosta 1", "1"),
            # city ma 65 znaków (limit kolumny to 64)
            ("Jan Kowalski", "Y" * 65, 30, "90010112345", "Prosta 1", "1"),
            # street ma 129 znaków (limit kolumny to 128)
            ("Jan Kowalski", "Warszawa", 30, "90010112345", "Z" * 129, "1"),
            # appNo ma 11 znaków (limit kolumny to 10)
            ("Jan Kowalski", "Warszawa", 30, "90010112345", "Prosta 1", "1" * 11),
            # PESEL ma 10 cyfr (o 1 za mało) lub 12 cyfr (o 1 za dużo)
            ("Jan Kowalski", "Warszawa", 30, "9001011234", "Prosta 1", "1"),
            ("Jan Kowalski", "Warszawa", 30, "900101123456", "Prosta 1", "1"),
            # Wiek na granicy: -1 lub nierealistyczne 151 lat
            ("Jan Kowalski", "Warszawa", -1, "90010112345", "Prosta 1", "1"),
            ("Jan Kowalski", "Warszawa", 151, "90010112345", "Prosta 1", "1"),
        ]

        for name, city, age, pesel, street, app_no in boundary_cases:
            with self.subTest(
                name_len=len(name),
                city_len=len(city),
                street_len=len(street),
                appNo_len=len(app_no),
                pesel_len=len(pesel),
                age=age,
            ):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=name,
                        city=city,
                        age=age,
                        pesel=pesel,
                        street=street,
                        appNo=app_no,
                    )


    def test_extreme_input(self):
        extreme_lengths = [10_000, 100_000, 1_000_000, 2_000_000, 4_000_000]

        for length in extreme_lengths:
            payload = "X" * length
            with self.subTest(length=length):
                with self.assertRaises((ValueError, TypeError)):
                    Customer(
                        name=payload,
                        city=payload,
                        age=30,
                        pesel="90010112345",
                        street=payload,
                        appNo="1",
                    )


if __name__ == "__main__":
    unittest.main()