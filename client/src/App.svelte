<!-- src/App.svelte -->
<script>
  let jobDescription = "";
  let resumeFile;
  let result;
  let error = "";

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.name.toLowerCase().endsWith('.tex')) {  // Changed to check file extension
        resumeFile = file;
        error = "";
      } else {
        error = "Please upload a .tex file";
        resumeFile = null;
      }
    };

  const submitForm = async () => {

    console.log('Submitting with:', { resumeFile, jobDescription });

    if (!resumeFile || !jobDescription) {
      error = "Please fill in all fields";
      return;
    }


    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("jobDescription", jobDescription);

    try {
      const response = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: formData
      });
      
      if (!response.ok) throw new Error('Server error');
      
      result = await response.json();
      error = "";
    } catch (err) {
      error = "Error submitting form: " + err.message;
    }
  };
</script>

<main>
  <h1>AI Resume Tailor</h1>
  
  <div class="form-container">
    <div class="input-group">
      <label for="resume">Upload Resume (.tex):</label>
      <input
        type="file"
        id="resume"
        accept=".tex"
        on:change={handleFileUpload}
        class:invalid={error && !resumeFile}
      />
    </div>

    <div class="input-group">
      <label for="jobDescription">Job Description:</label>
      <textarea
        id="jobDescription"
        bind:value={jobDescription}
        rows="5"
      ></textarea>
    </div>

    <button on:click={submitForm}>Analyze</button>

    {#if error}
      <div class="error">{error}</div>
    {/if}

    {#if result}
      <div class="result">
        <h2>Analysis Result:</h2>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </div>
    {/if}
  </div>
</main>

<style>
  .form-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .input-group {
    margin-bottom: 20px;
  }

  .invalid {
    border: 2px solid red;
    border-radius: 4px;
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
  }

  input[type="file"] {
    margin-bottom: 10px;
  }

  textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    background-color: #4CAF50;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:hover {
    background-color: #45a049;
  }

  .error {
    color: red;
    margin-top: 15px;
  }

  .result {
    margin-top: 20px;
    padding: 15px;
    background-color: #555555;
    border-radius: 4px;
  }
</style>
