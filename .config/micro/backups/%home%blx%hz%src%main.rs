use std::io;

fn main() {
    println!("Как вас зовут?");

    let mut name = String::new();

    io::stdin()
        .read_line(&mut name)
        .expect("Не удалось прочитать строку");

    let name = name.trim();

    // Проверяем, что строка не пустая
    if name.is_empty() {
        eprintln!("Ошибка: имя не может быть пустым!");
        std::process::exit(1); // Завершаем программу с кодом ошибки 1
    }

    println!("Привет, {}!", name);
}
