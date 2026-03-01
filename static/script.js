document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch options from the backend (API) when the page loads
    try {
        const response = await fetch("/options");
        const data = await response.json();

        // Add body parts to the dropdown list
        const bodyPartSelect = document.getElementById("bodyPart");
        data.body_parts.forEach(part => {
            const option = document.createElement("option");
            option.value = part;
            // Capitalize the first letter for better UI
            option.textContent = part.charAt(0).toUpperCase() + part.slice(1);
            bodyPartSelect.appendChild(option);
        });

        // Add equipment options as checkboxes
        const equipmentList = document.getElementById("equipmentList");
        data.equipment.forEach(eq => {
            const div = document.createElement("div");
            div.innerHTML = `
                <input type="checkbox" id="eq_${eq}" value="${eq}" checked>
                <label for="eq_${eq}">${eq}</label>
            `;
            equipmentList.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading options:", error);
    }

    // 2. Code to execute when the "Generate Workout" button is clicked
    document.getElementById("generateBtn").addEventListener("click", async () => {
        const bodyPart = document.getElementById("bodyPart").value;
        const numExercises = parseInt(document.getElementById("numExercises").value);

        // Get only the checked equipment values
        const checkedEquipments = Array.from(document.querySelectorAll('#equipmentList input:checked'))
                                     .map(cb => cb.value);

        if (checkedEquipments.length === 0) {
            alert("Please select at least one equipment!");
            return;
        }

        // Prepare the payload to send to the API
        const requestData = {
            body_part: bodyPart,
            equipment_list: checkedEquipments,
            num_exercises: numExercises
        };

        try {
            // Send the data to the engine via POST request
            const response = await fetch("/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            });

            const resultsDiv = document.getElementById("results");

            // Show an error message if no matching exercises are found
            if (!response.ok) {
                resultsDiv.innerHTML = `<p style="color: red;">No exercises found for these criteria.</p>`;
                return;
            }

            const workoutPlan = await response.json();

            // Convert the received JSON data into an HTML table
            let html = `<h3>Your Workout Plan</h3>
                        <table border="1" style="width:100%; text-align:left; border-collapse: collapse;">
                            <tr>
                                <th>Exercise Name</th>
                                <th>Equipment</th>
                                <th>Type</th>
                            </tr>`;

            workoutPlan.forEach(exercise => {
                html += `<tr>
                            <td>${exercise.name}</td>
                            <td>${exercise.equipment}</td>
                            <td>${exercise.exercise_type || '-'}</td>
                         </tr>`;
            });
            html += `</table>`;

            // Render the table on the screen
            resultsDiv.innerHTML = html;

        } catch (error) {
            console.error("Error generating workout:", error);
        }
    });
});