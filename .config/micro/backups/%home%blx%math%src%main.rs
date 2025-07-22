use rand::Rng;
use std::io::{self, Write};

fn main() {
    println!("Answer on question or you idiot");

    loop {
        let a = rand::thread_rng().gen_range(0..=100);
        let b = rand::thread_rng().gen_range(0..=100);
        let is_addition = rand::thread_rng().gen_bool(0.5);

        let (question, correct_answer) = if is_addition {
            (format!("{a} + {b} = "), a + b)
        } else {
            let (max, min) = if a >= b { (a, b) } else { (b, a) };
            (format!("{max} - {min} = "), max - min)
        };

        print!("{} ", question);
        io::stdout().flush().unwrap();

        let mut input = String::new();
        if let Err(_) = io::stdin().read_line(&mut input) {
            println!("Uncorrect. retry idiot!");
            continue;
        }

        let trimmed = input.trim();
        if trimmed.eq_ignore_ascii_case("exit") || trimmed.eq_ignore_ascii_case("q") {
            println!("Goodbye world!");
            break;
        }

        match trimmed.parse::<i32>() {
            Ok(answer) if answer == correct_answer => {
                println!("Correct!");
            }
            Ok(_) => {
                println!("You stupid Uncorrect: {}", correct_answer);
            }
            Err(_) => {
                println!("type 'exit' to  quite the game.");
            }
        }

        println!();
    }
}
