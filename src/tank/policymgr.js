
var app = angular.module('app', []);

/* app.config(function($locationProvider) {
	$locationProvider.html5Mode(true);
}); */

app.filter('escape', function() {
	return window.encodeURIComponent;
});

app.controller('TanksCtrl', ['$scope', '$http', function($scope, $http) {
	var currentUser = tiddlyweb.status.username;

	$http.get('/bags?select=policy:create',
		{headers: {'Accept': 'application/json'}})
		.success(function(data) {
			$scope.tanks = data;
	});
}]);

app.controller('TankCtrl',
	['$scope', '$location', '$http', function($scope, $location, $http) {
	$scope.constraints = ['manage', 'read', 'write', 'create', 'delete'];
	$scope.$watch(function() { return $location.path();}, 
		function(path) {
			if (path) {
				var tankName = path.split('/')[1];
				if (tankName) {
					$http.get('/bags/' + encodeURIComponent(tankName),
						{headers: {'Accept': 'application/json'}})
						.success(function(data) {
							angular.extend(data, {name: tankName});
							$scope.tank = data;
						});
				}
			}
		});
}]);
