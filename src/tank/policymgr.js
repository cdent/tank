
var app = angular.module('app', []);

app.filter('escape', function() {
	return window.encodeURIComponent;
});

app.factory('tankService', function($http, $q) {
	var tanks;
	return {
		getTanks: function(callback) {
			if (tanks) {
				callback(tanks);
			} else {
				$http.get('/bags.json?select=policy:create')
					.then(function(res) {
						var bags = res.data;
						var resources = bags.map(function(name) {
							var uri = '/bags/' + encodeURIComponent(name);
							return $http.get(uri,
								{headers: {'Accept': 'application/json'}});
						});
						return $q.all(resources);
					})
					.then(function(res) {
						var data = {};
						res.forEach(function(res) {
							var tankName = res.config.url
								.replace(/\/bags\/([^\/]+)/, "$1");
							angular.extend(res.data, {name: tankName});
							data[tankName] = res.data;
						});
						tanks = data;
						callback(tanks);
					});
			}
		}
	};
});

app.controller('TanksCtrl', function($scope, tankService) {
	tankService.getTanks(function(data) {
		$scope.tanks = data;
	});
});

app.controller('TankCtrl', function($scope, $location, tankService) {
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];

	function setData(tankName) {
		tankService.getTanks(function(data) {
			$scope.tanks = data;
			$scope.tank = $scope.tanks[tankName];
		});
	}

	$scope.$watch(function() { return $location.path();}, 
		function(path) {
			if (path) {
				var tankName = path.split('/')[1];
				if (tankName) {
					setData(tankName);
				}
			}
		}
	);

	$scope.startEditor = function() {};

});
