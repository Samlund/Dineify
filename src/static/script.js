document.getElementById("generator_btn").addEventListener('click', generatorBtn);

//Validation when user pressed the button "Enter" and sends request to backend
async function generatorBtn() {
    try {
        const selectedCuisine = getSelectedCuisine();

        if (!selectedCuisine || selectedCuisine === "Open to select cuisine") {
            alert('Please select cuisine.');
            return;
        }
        const recipes = await fetchRecipes(selectedCuisine);
        const id = await fetchId(selectedCuisine);
        displayRecipe(recipes.menu);
        displayPlaylist(id);

    } catch (error) {
        console.error("Error fetching recipes:", error);
        alert("Please try again");
    }
}

// Get selected cuisine
function getSelectedCuisine() {
    const cuisineSelection = document.querySelector("#search_generator select");
    return cuisineSelection.value;
}

//Sends request to to backend to get recipes
async function fetchRecipes(cuisine) {
    const header = new Headers();
        header.append("Accept", "application/json");
    try {
        const response = await fetch(`/v1.0/recipes/?cuisine=${cuisine}`, {
            headers: header
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}

async function fetchId(cuisine) {
    const header = new Headers();
        header.append("Accept", "application/json");
    try {
        const response = await fetch(`/v1.0/playlists/?theme=${cuisine}`, {
            headers: header
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}

//Assign content to right HTML element
function displayRecipe(dishes) {
    dishes.forEach(recipe => {
        const courseDiv = document.getElementById(`course_${recipe.course}`);
        if (courseDiv) {
            generateCourse(courseDiv, recipe);
        } else {
            console.warn(`Course_${recipe.course} could not be found.`);
        }
    });
}

function displayPlaylist(id) {
    document.getElementById("embedded_player").src = `https://open.spotify.com/embed/playlist/${id}?utm_source=generator`;
}

//Adding content to assigned element
function generateCourse(courseDiv, recipe) {
    const header = courseDiv.querySelector(`#${recipe.course}_header`);
    const img = courseDiv.querySelector(`#${recipe.course}_img`);
    const ingredients = courseDiv.querySelector(`#${recipe.course}_ingredients`);
    const instructions = courseDiv.querySelector(`#${recipe.course}_instructions`);
    const summary = courseDiv.querySelector(`#${recipe.course}_summary`);

    if (header) {
        header.innerText = `Title: ${recipe.title}, URL: ${recipe.url}, Course: ${recipe.course}, Servings: ${recipe.servings}, Ready In: ${recipe.readyInMinutes} minutes`;
    } else {
        console.warn(`${recipe.course}_header was not found.`);
    }

    if (img) {
        img.src = recipe.image;
        img.alt = `${recipe.course} image`;
    } else {
        console.warn(`${recipe.course}_img was not found.`);
    }

    if (ingredients) {
        ingredients.innerText = `Ingredients: ${recipe.ingredients.map(ing => `${ing.name} (${ing.amount} ${ing.unit})`).join(', ')}`;
    } else {
        console.warn(`${recipe.course}_ingredients was not found.`);
    }

    if (instructions) {
        instructions.innerHTML = `Instructions: ${recipe.instructions}`;
    } else {
        console.warn(`${recipe.course}_instructions was not found.`);
    }

    if (summary) {
        summary.innerHTML = `Summary: ${recipe.summary}`;
    } else {
        console.warn(`${recipe.course}_summary was not found.`);
    }
}
