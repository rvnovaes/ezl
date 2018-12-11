class Geolocation {
	constructor() {
		this.latitude;
		this.longitude;
		this.error;
		this.getLocation();
	}

	getLocation() {
	    if (navigator.geolocation) {	        
	        navigator.geolocation.getCurrentPosition((position)=>{
	        	this.latitude = position.coords.latitude;
	        	this.longitude = position.coords.longitude;
	        }, (error)=>{
	        	this.showError(error);
	        });
	    } else {
	        console.log("Geolocalização não é suportada pelo browser.");
	    }		
	}
	showError(error) {      
        switch(error.code) {
            case error.PERMISSION_DENIED:
                console.log("O usuário negou o acesso à Geolocalização.");
                break;
            case error.POSITION_UNAVAILABLE:
                console.log("Informação de localização não disponível.");
                break;
            case error.TIMEOUT:
                console.log("Tempo limite atingido para o pedido de localização.");
                break;
            case error.UNKNOWN_ERROR:
                console.log("Ocorreu um erro desconhecido.");
                break;
        }
	}
}