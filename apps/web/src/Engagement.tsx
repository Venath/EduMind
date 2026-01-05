const Engagement = () => {
  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <iframe
        src="http://localhost:8002/app/index.html"
        title="Engagement Tracker"
        style={{
          width: "100%",
          height: "100%",
          border: "none",
        }}
      />
    </div>
  )
}

export default Engagement
