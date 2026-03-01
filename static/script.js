document.addEventListener("DOMContentLoaded", async () => {
    // 1. Fetch updated options
    try {
        const response = await fetch("/options");
        if (!response.ok) throw new Error("Failed to fetch options");
        const data = await response.json();

        const splitSelect = document.getElementById("splitName");
        splitSelect.innerHTML = ""; 
        data.splits.forEach(split => {
            const option = document.createElement("option");
            option.value = split;
            option.textContent = split;
            splitSelect.appendChild(option);
        });

        const volumeSelect = document.getElementById("volumeLevel");
        volumeSelect.innerHTML = ""; 
        data.volumes.forEach(vol => {
            const option = document.createElement("option");
            option.value = vol;
            option.textContent = vol;
            if(vol === "Low") option.selected = true;
            volumeSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error loading options:", error);
    }

    // 2. Generate Plan Button Click
    document.getElementById("generateBtn").addEventListener("click", async () => {
        const splitName = document.getElementById("splitName").value;
        const volumeLevel = document.getElementById("volumeLevel").value;
        const selectedProfile = document.getElementById("equipmentProfile").value;

        const requestData = {
            split_name: splitName,
            equipment_profile: selectedProfile,
            volume_level: volumeLevel
        };

        try {
            const response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestData)
            });

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = ""; 
            
            // Hide action buttons and chart area initially
            document.getElementById("actionButtons").style.display = "none";
            document.getElementById("chartContainer").innerHTML = "";

            if (!response.ok) {
                resultsDiv.innerHTML = `<p style="color: red;">No exercises found for these criteria. Try a different equipment profile.</p>`;
                return;
            }

            const weeklyPlan = await response.json();

            // 3. Render Weekly Plan as Cards
            for (const [day, exercises] of Object.entries(weeklyPlan)) {
                const dayCard = document.createElement("div");
                dayCard.className = "day-card";

                let html = `<h3>${day}</h3>`;

                if (typeof exercises === "string") {
                    html += `<p class="rest-msg">${exercises}</p>`;
                } else {
                    html += `<table>
                                <tr>
                                    <th>Exercise</th>
                                    <th>Target</th> 
                                    <th>Sets/Reps</th>
                                    <th>Tool</th>
                                    <th>Action</th>
                                </tr>`;
                    exercises.forEach((ex, index) => {
                        const rowId = `row_${day.replace(/\s+/g, '')}_${index}`;
                        html += `<tr id="${rowId}">
                                    <td class="ex-name">${ex.name}</td>
                                    <td class="ex-target" style="color: #b3b3b3; font-size: 0.9rem;">${ex.target}</td> 
                                    <td><strong>${ex.volume}</strong></td>
                                    <td class="ex-eq">${ex.equipment}</td>
                                    <td>
                                        <button class="swap-btn" onclick="swapExercise('${day}', ${index}, '${ex.name}', '${rowId}')">🔄</button>
                                    </td>
                                 </tr>`;
                    });
                    html += `</table>`;
                }

                dayCard.innerHTML = html;
                resultsDiv.appendChild(dayCard);
            }

            // 4. Show action buttons and store plan globally
            document.getElementById("actionButtons").style.display = "block";
            window.currentWeeklyPlan = weeklyPlan;

        } catch (error) {
            console.error("Error generating plan:", error);
        }
    });

    // 5. Weekly Analysis (Chart) Button Click
    document.getElementById("analyzeBtn").addEventListener("click", async () => {
        try {
            const response = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(window.currentWeeklyPlan)
            });
            const data = await response.json();

            const chartDiv = document.getElementById("chartContainer");
            chartDiv.innerHTML = `<img src="${data.chart}" alt="Volume Chart" style="max-width: 100%; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); margin-top: 15px;">`;
            chartDiv.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error("Error analyzing plan:", error);
        }
    });

    // 6. Export PDF Button Click
    document.getElementById("pdfBtn").addEventListener("click", async () => {
        try {
            const response = await fetch("/export-pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(window.currentWeeklyPlan)
            });
            const data = await response.json();

            const link = document.createElement('a');
            link.href = data.download_url;
            link.download = 'GainEngine_Workout_Plan.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error("Error generating PDF:", error);
        }
    });
});

async function swapExercise(day, index, exerciseName, rowId) {
    const selectedProfile = document.getElementById("equipmentProfile").value;
    const dayCard = document.getElementById(rowId).closest('.day-card');
    const currentExercises = Array.from(dayCard.querySelectorAll('.ex-name')).map(td => td.textContent);

    try {
        const response = await fetch("/swap", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                exercise_name: exerciseName,
                equipment_profile: selectedProfile,
                current_day_exercises: currentExercises
            })
        });

        if (response.ok) {
            const newEx = await response.json();
            
            // Old Exercise ➔ New Exercise
            const confirmSwap = confirm(`${exerciseName} ➔ ${newEx.name}`);

            if (confirmSwap) {
                const row = document.getElementById(rowId);
                row.querySelector(".ex-name").textContent = newEx.name;
                row.querySelector(".ex-target").textContent = newEx.target;
                row.querySelector(".ex-eq").textContent = newEx.equipment;
                
                const btn = row.querySelector(".swap-btn");
                btn.setAttribute("onclick", `swapExercise('${day}', ${index}, '${newEx.name}', '${rowId}')`);
                
                row.style.backgroundColor = "#3d3d3d";
                setTimeout(() => row.style.backgroundColor = "transparent", 1000);
            }
        } else {
            alert("No alternative found for this exercise with your current equipment.");
        }
    } catch (error) {
        console.error("Error during smart swap:", error);
    }
}
