
var app = angular.module('app', []);

app.filter('escape', function() {
	return window.encodeURIComponent;
});

app.service('tankService', function($http, $q) {
	var tanks;
	this.getTanks = function() {
		if (tanks) { // previously cached
			return tanks;
		}
		tanks = $http.get('/bags.json?select=policy:manage')
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
				return data;
			});
		return tanks;
	};
});

app.controller('TanksCtrl', function($scope, tankService) {
	tankService.getTanks.then(function(data) {
		$scope.tanks = [];
		angular.forEach(data, function(value, key) {
			$scope.tanks.push(value);
		});
	});
});

app.controller('TankEditor', function($scope, $http, $rootScope) {
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];
	$scope.$on('startEdit', function(ev, data) {
		$scope.editTank = angular.copy(data.tank);
		$scope.originalData = angular.copy(data.tank);
	});

	$scope.$on('clearEdit', function() {
		$scope.editTank = null;
	});

	$scope.cancelEditor = function() {
		$scope.editTank = null;
		$rootScope.$broadcast('finishEdit', {tank: $scope.originalData});
	};

	// XXX: move to service?
	$scope.saveTank = function() {
		var uri = '/bags/' + encodeURIComponent($scope.editTank.name);
		$http.put(uri, $scope.editTank, {headers: {'Accept': 'application/json'}})
			.success(function() {
				$rootScope.$broadcast('finishEdit', {
					tank: angular.copy($scope.editTank)});
				$scope.editTank = null;
			});
	};

});

app.controller('TankCtrl', function($scope, $location, $rootScope, tankService) {
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];

	function setData(tankName) {
		tankService.getTanks.then(function(data) {
			$scope.tanks = data;
			$scope.tank = angular.copy($scope.tanks[tankName]);
		});
	}

	$scope.$watch(function() { return $location.path();}, 
		function(path) {
			if (path) {
				var tankName = path.split('/')[1];
				if (tankName) {
					$rootScope.$broadcast('clearEdit');
					setData(tankName);
				}
			}
		}
	);

	$scope.$on('finishEdit', function(ev, data) {
		if (data) {
			$scope.tank = angular.copy(data.tank);
			$scope.tanks[$scope.tank.name] = $scope.tank;
		}
	});

	$scope.startEditor = function() {
		$rootScope.$broadcast('startEdit', {tank: $scope.tank});
		$scope.tank = null;
	};

});
