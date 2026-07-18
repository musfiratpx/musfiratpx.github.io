

/*  planet.forEach(planet => { //for each element in planets class, 
        planet.addEventListener('click', () => { //add an event listener method


            switch(planet.id){
                case 'earth':
                case 'jupiter':
                case 'mars':
                case 'neptune':
                case 'saturn':
                case 'uranus':
                default:

            }




        });




    });

    */


/*
for(int i = 0; i < planets.size(); i++){
    planets.get(i).addMouseListener(new MouseAdapter() {
        @Override public void mousePressed(MouseEvent e){
            System.out.println("This is " + planets.get(i).getId());
        }
    })
}  -> how i would write in java
*/

//steps: 
//communicate with flask. Tells backend, hey this planet has been clicked --> sends a number
//Flask sees that number and tells Python/AI backend to generate info based on that number (planet)
//Python tells Flask, it has successfully generated it, now go tell Javascript. 
//Flask tells Javascript the generation is done, now update the UI
//Javascript creates a popup with ai generated overview using HTML and CSS styling.


//check what planet is clicked. 
function PlanetMessage(){
    //look at the html document, specifically at the class planets
    const planets = document.querySelectorAll('.planets div, .planets img'); //all div elements in planets class, all img elements
    for(const planet of planets){ //for all div elements and all img elements
        planet.addEventListener('click', () =>{ //add a click listener that says this.
            alert("This is " + planet.id); // say "This is (name of planet)"
        

        });
    }

}
PlanetMessage(); //call function or else it won't run. 




// check if puddle overlaps with any planet



function overlapsWithPlanets(x, y, size) {
    const planets = document.querySelectorAll('.planets div, .planets img');
    
    for (let planet of planets) {
        const rect = planet.getBoundingClientRect();
        
        // planet boundaries by 30px 
        const buffer = 30;
        const pLeft = rect.left - buffer;
        const pRight = rect.right + buffer;
        const pTop = rect.top - buffer;
        const pBottom = rect.bottom + buffer;

        // check collisions
        if (x < pRight && x + size > pLeft && y < pBottom && y + size > pTop) {
            return true; 
        }
    }
    return false; 
}

function createPuddle() {
    const container = document.getElementById('puddle-container');
    if (!container) return;

    const puddle = document.createElement('div');
    puddle.classList.add('space-puddle');

    // set the size of the puddle
    const size = Math.floor(Math.random() * 50) + 50; // 50px to 100px
    puddle.style.width = `${size}px`;
    puddle.style.height = `${size}px`;

    // loop until we find coordinates that do not hit a planet
    let randomX = 0;
    let randomY = 0;
    let attempts = 0;
    let keepTrying = true;

    while (keepTrying && attempts < 100) {
        randomX = Math.floor(Math.random() * (window.innerWidth - size));
        randomY = Math.floor(Math.random() * (window.innerHeight - size));
        
        // no overlap= break the loop
        if (!overlapsWithPlanets(randomX, randomY, size)) {
            keepTrying = false;
        }
        attempts++;
    }

    puddle.style.left = `${randomX}px`;
    puddle.style.top = `${randomY}px`;

    // make puddle shape
    const r1 = Math.floor(Math.random() * 20) + 40; 
    const r2 = 100 - r1;
    const r3 = Math.floor(Math.random() * 20) + 40;
    const r4 = 100 - r3;
    puddle.style.borderRadius = `${r1}% ${r2}% ${r3}% ${r4}% / ${r3}% ${r1}% ${r2}% ${r4}%`;

    // random color
    const randomHue = Math.floor(Math.random() * 360);
    puddle.style.filter = `hue-rotate(${randomHue}deg)`;

    // interactiveness
    puddle.addEventListener('click', () => {
        alert("This is a space puddle"); 
        puddle.remove();
    });

    container.appendChild(puddle);

    // Auto-cleanup after 10s if left unclicked
    setTimeout(() => {
        if (puddle.parentNode) puddle.remove();
    }, 10000);
}

createPuddle();
setInterval(createPuddle, 10000);