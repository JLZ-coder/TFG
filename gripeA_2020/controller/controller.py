class controller:
    def __init__(self, model, dataFact):
        self.model
		self.dataFact = dataFact

	def loadParams(self):
	# public void loadBodies(InputStream in) {
	# 	JSONObject jsonInput = new JSONObject(new JSONTokener(in));
	# 	JSONArray ja = jsonInput.getJSONArray("bodies");
		
	# 	for (int i = 0; i < ja.length(); i++) {
	# 		_sim.addBody(_factor.createInstance(ja.getJSONObject(i)));	//coge cada JSON, lo convierte a body y lo anade al simulador
	# 	}
	# }

	def run(self):
		self.model.advance()
	
	public void run(int n, OutputStream out){
		PrintStream p = (out == null) ? null : new PrintStream(out);
		
		p.println("{");
		p.println("\"states\": [");
		p.println(_sim.toString() + ",");
		
		for (int i = 1; i < n; i++) {
			_sim.advance();
			p.println(_sim.toString() + ",");
		}
		_sim.advance();
		p.println(_sim.toString());
		p.println("]");
		p.println("}");
		
		p.close();
	}

	public void setDeltaTime(double dt) {
		_sim.setDeltaTime(dt);
	}

	public Factory<GravityLaws> getGravityLawsFactory(){
		return _gl;
	}
	
	public void setGravityLaws(JSONObject info) {
		_sim.setGravityLaws(_gl.createInstance(info));
	}