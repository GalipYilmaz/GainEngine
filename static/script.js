document.addEventListener("DOMContentLoaded", async () => {
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
            if(vol === "Normal") option.selected = true;
            volumeSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading options:", error);
    }

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

            if (!response.ok) {
                resultsDiv.innerHTML = `<p style="color: red;">No exercises found for these criteria.</p>`;
                return;
            }

            const weeklyPlan = await response.json();

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
                                    <td class="ex-target" style="color: #b3b3b3;">${ex.target}</td>
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
        } catch (error) {
            console.error("Error generating plan:", error);
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

            // YENİ VE SADELEŞTİRİLMİŞ ONAY KUTUSU (Eski -> Yeni)
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