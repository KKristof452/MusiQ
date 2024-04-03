class Test:
    def __init__(self, name, age, school) -> None:
        self.name = name
        self.age = age
        self.school = school

tests = [Test("jozsi", 12, "asd"), Test("Sanyi", 32, "xcv"), Test("Adrienn", 25, "ert")]

for test in tests:
    if (test.name, test.age) == ("Sanyi", 32):
        print("ulalal")
    else:
        print("eff")
