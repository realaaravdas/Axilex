use krystal_parser::KrystalParser;
use std::fs;

fn main() {
    let krystal_file = "../examples/hello_krystal.krystal";
    let source = fs::read_to_string(krystal_file).expect("Failed to read file");
    
    println!("Testing parser on: {}", krystal_file);
    println!("Source length: {} bytes\n", source.len());
    
    match KrystalParser::validate_syntax(&source) {
        Ok(()) => println!("✓ Syntax validation passed!"),
        Err(e) => eprintln!("✗ Syntax error: {}", e),
    }
}
