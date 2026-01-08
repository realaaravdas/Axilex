use krystal_parser::KrystalSimplifier;

fn main() {
    let source = r#"
# Test file with redundant operations
cube(0, 0, 0, 10)



translate(0, 0, 0) {
    sphere(5, 5, 5, 3)
}

# @noformat
# This section should not be simplified
translate(0, 0, 0) {
    cylinder(2, 2, 2, 1, 5)
}
# @noformat_end

scale(1, 1, 1) {
    cube(10, 10, 10, 8)
}
"#;

    println!("=== Original Code ===");
    println!("{}", source);
    
    let simplifier = KrystalSimplifier::with_default();
    match simplifier.simplify(source) {
        Ok(simplified) => {
            println!("\n=== Simplified Code ===");
            println!("{}", simplified);
            
            println!("\n=== Analysis ===");
            if simplified.contains("translate(0, 0, 0)") {
                println!("✓ Protected translate(0,0,0) was preserved");
            }
            if !simplified.contains("scale(1, 1, 1)") {
                println!("✓ Redundant scale(1,1,1) was removed");
            }
            if !simplified.contains("\n\n\n") {
                println!("✓ Excessive whitespace was normalized");
            }
        }
        Err(e) => eprintln!("Error: {}", e),
    }
}
