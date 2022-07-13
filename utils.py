class Frequency:
    file_name = 'frequency.txt'

    @classmethod
    def save_frequency(cls, frequency: str):
        with open(cls.file_name, 'w',  encoding='utf-8') as f:
            f.write(frequency)

    @classmethod
    def load_frequency(cls) -> int:
        with open(cls.file_name, 'r', encoding='utf-8') as f:
            return int(f.read().strip())
